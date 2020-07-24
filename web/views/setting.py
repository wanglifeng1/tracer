from django.shortcuts import render, redirect
from web import models
from web.utils.tencent.cos import delete_bucket


def setting(request, project_id):
    return render(request, 'web/setting.html')


def setting_delete(request, project_id):
    """ 删除项目 """
    if request.method == "GET":
        return render(request, 'web/setting_delete.html')

    # 拿到要删除的项目名
    project_name = request.POST.get('project_name')
    print("project_name", project_name)
    # 判断项目名称是否存在
    if not project_name or project_name != request.tracer.project.name:
        return render(request, 'web/setting_delete.html', {"error": "项目名错误"})
    # 只有创建者才可以删除项目
    if request.tracer.user != request.tracer.project.creator:
        return render(request, 'web/setting_delete.html', {"error": "只有项目创建者可删除项目"})

    # 删除项目
    # 1. 删除cos中的项目
    # 2. 删除数据库中的项目
    delete_bucket(bucket=request.tracer.project.bucket, region=request.tracer.project.region)
    models.Project.objects.filter(id=project_id).delete()

    return redirect('web:project_list')