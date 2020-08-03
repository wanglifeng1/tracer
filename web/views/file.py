import json
import requests
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, HttpResponse
from django.forms import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import escape_uri_path
from web.forms.file import FolderForm, FileForm
from web import models
from web.utils.tencent.cos import cos_delete, cos_deletes, credential


# http://127.0.0.1:8001/web/manage/9/file/
# http://127.0.0.1:8001/web/manage/9/file/?foler=9
def file(request, project_id):
    """ 文件夹列表 & 添加文件夹 """
    parent_obj = None
    folder_id = request.GET.get("folder", "")
    if folder_id.isdecimal():
        parent_obj = models.FileRegister.objects.filter(id=int(folder_id), type=1, project_id=project_id).first()
    # get请求，文件夹列表
    if request.method == "GET":
        parent = parent_obj
        breadcrumb_list = []
        while parent:
            # breadcrumb_list.insert(0, {"id": parent.id, "name": parent.name})
            breadcrumb_list.insert(0, model_to_dict(parent, ['id', 'name']))
            parent = parent.parent

        # 获取当前目录下的所有文件 & 文件夹
        file_list = models.FileRegister.objects.filter(parent=parent_obj, project_id=project_id).order_by('type')

        form = FolderForm(request, parent_obj)
        context = {
            "form": form,
            "file_list": file_list,
            "breadcrumb_list": breadcrumb_list,
            "parent": parent_obj
        }
        return render(request, 'web/file.html', context)

    # POST请求，添加或修改文件夹
    # 判断新建 / 修改
    fid = request.POST.get("fid")
    if fid.isdecimal():
        # 修改
        edit_obj = models.FileRegister.objects.filter(id=int(fid), type=1, project_id=project_id).first()
        form = FolderForm(request, parent_obj, data=request.POST, instance=edit_obj)
    else:
        # 新建
        form = FolderForm(request, parent_obj, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.update_user = request.tracer.user
        form.instance.type = 1
        form.instance.parent = parent_obj
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


# http://127.0.0.1:8001/web/manage/9/file/?foler=9
def file_delete(request, project_id):
    """ 删除 文件 & 文件夹 （cos同步删除）"""
    # 判断文件/文件夹
    fid = request.GET.get("fid")
    # 获取当前fid对象
    obj = models.FileRegister.objects.filter(id=fid, project_id=project_id).first()
    # 判断对象类型 文件/文件夹分开处理
    if obj.type == 2:
        # 删除文件 （包括数据库 cos 已使用空间归还）
        # 归还已使用空间
        request.tracer.project.use_space -= obj.file_size
        request.tracer.project.save()
        # 删除cos数据
        cos_delete(request.tracer.project.bucket, request.tracer.project.region, obj.key)
    else:
        # 删除文件夹 统计出所有释放的空间 并归还
        # 定义空列表，存放当前目录以及子目录下边的所有文件夹
        folder_list = [obj, ]
        total_size = 0
        key_list = []
        # 1. 循环当前目录
        for folder in folder_list:
            child_list = models.FileRegister.objects.filter(project_id=project_id, parent=folder).order_by('type')
            for child in child_list:
                if child.type == 1:   # 文件夹 放入列表
                    folder_list.append(child)
                else:        # 文件 文件大小加到total_size, 文件key放到key_list 方便批量删除
                    total_size += child.file_size
                    key_list.append({"key": child.key})
        if key_list:  # 2. 批量删除
            cos_deletes(request.tracer.project.bucket, request.tracer.project.region, key_list)
        if total_size:   # 3. 归还已使用空间
            request.tracer.project.use_space -= total_size
            request.tracer.project.save()
    # 从数据库删除
    obj.delete()
    return JsonResponse({"status": True})


@csrf_exempt
def cos_credential(request, project_id):
    """ 获取临时凭证 """
    # 获取要上传的文件列表
    file_list = json.loads(request.body.decode('utf-8'))
    pre_file_limit = request.tracer.price_policy.project_size * 1024 * 1024
    # 项目空间
    project_space = request.tracer.price_policy.project_space * 1024 * 1024 * 1024
    # 项目已使用空间
    project_use_space = request.tracer.project.use_space
    total_size = 0
    # 限制文件处理 单文件 & 总大小
    for file in file_list:
        # 文件名 file['name']
        # 文件大小 file['size']
        if file['size'] > pre_file_limit:
            msg = "单文件超出限制，文件：{}，限制大小{}，请升级套餐".format(file['name'], pre_file_limit)
            return JsonResponse({"status": False, "error": msg})
        total_size += file['size']
    # 文件总大小判断
    if total_size > project_space - project_use_space:
        return JsonResponse({"status": False, "error": "文件总大小超出限制，请升级套餐"})
    dic = credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({"status": True, "data": dic})


@csrf_exempt
def file_post(request, project_id):
    """ 文件上传 """
    # 获取前端数据，进行校验(使用form表单校验)
    form = FileForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过，数据写入数据库
        data_dic = form.cleaned_data
        data_dic.pop('etag')
        data_dic.update({"project": request.tracer.project, "type": 2, "update_user": request.tracer.user})
        instance = models.FileRegister.objects.create(**data_dic)
        # 更新项目已使用空间
        request.tracer.project.use_space += data_dic['file_size']
        request.tracer.project.save()
        # 拿到这条数据，传给前端 进行展示
        result = {
            'id': instance.id,
            'name': instance.name,
            'file_size': instance.file_size,
            'update_user': instance.update_user.name,
            'update_time': instance.update_time.strftime('%Y年%m月%d日 %H:%M'),
            'download_url': reverse('web:file_download', kwargs={"project_id": project_id, "file_id": instance.id})
        }
        return JsonResponse({"status": True, "data": result})
    return JsonResponse({"status": False, "error": form.errors})


def file_download(request, project_id, file_id):
    """ 文件下载 """
    file_obj = models.FileRegister.objects.filter(id=file_id, project_id=project_id).first()
    res = requests.get(file_obj.file_path)

    # 文件分块处理
    data = res.iter_content()
    # 提示下载框
    response = HttpResponse(data, content_type='application/octet-steam')

    # 设置响应头 中文文件名转义
    response['Content-Disposition'] = "attachment; filename={}".format(escape_uri_path(file_obj.name))
    return response
