import time
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web.forms.project import ProjectForm
from web import models

from web.utils.tencent.cos import create_bucket


def project_list(request):
    """ 后台管理展示 """
    if request.method == "GET":
        """ 得到三个列表 """
        project_dic = {"star": [], "my": [], "join": []}
        # 获取展示的项目
        # 1. 获取我创建的项目
        my_project_list = models.Project.objects.filter(creator=request.tracer.user)
        for item in my_project_list:
            if item.star:
                project_dic["star"].append({"value": item, "type": "my"})
            else:
                project_dic["my"].append(item)
        # 2. 获取参与的项目
        join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
        for item in join_project_list:
            if item.star:
                project_dic["star"].append({"value": item.project, "type": "join"})
            else:
                project_dic["join"].append(item.project)

        form = ProjectForm(request)
        return render(request, "web/project_list.html", {"form": form, "project_dic": project_dic})
    form = ProjectForm(request, data=request.POST)
    if form.is_valid():
        # 创建项目同时创建桶 & 区域
        name = form.cleaned_data.get('name')
        bucket = "{}-{}-{}-1300113042".format(name, request.tracer.user.mobile_phone, str(int(time.time())))
        region = "ap-beijing"
        create_bucket(bucket, region)
        # 保存到数据库
        form.instance.bucket = bucket
        form.instance.region = region
        # 校验通过，保存到数据库之前，还有一个必填字段，在form表单校验时没有
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def project_star(request, project_type, project_id):
    """ 星标 """
    if project_type == "my":
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=True)
        return redirect("web:project_list")
    elif project_type == "join":
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=True)
        return redirect("web:project_list")
    return HttpResponse("星标错误")


def project_unstar(request, project_type, project_id):
    """ 取消星标 """
    if project_type == "my":
        models.Project.objects.filter(id=project_id, creator=request.tracer.user).update(star=False)
        return redirect("web:project_list")
    elif project_type == "join":
        models.ProjectUser.objects.filter(project_id=project_id, user=request.tracer.user).update(star=False)
        return redirect("web:project_list")
    return HttpResponse("取消星标错误")
