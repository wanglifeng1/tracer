from django.http import JsonResponse
from django.shortcuts import render
from django.forms import model_to_dict
from web.forms.file import FolderForm
from web import models
from web.utils.tencent.cos import cos_delete, cos_deletes


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
            "breadcrumb_list": breadcrumb_list
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



