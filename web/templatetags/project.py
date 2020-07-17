from django.template import Library
from django.urls import reverse
from web import models


register = Library()


@register.inclusion_tag("inclousion/all_project.html")
def all_project_list(request):
    # 1. 获取我创建的项目
    my_project_list = models.Project.objects.filter(creator=request.tracer.user)
    # 2. 获取我参与的项目
    join_project_list = models.ProjectUser.objects.filter(user=request.tracer.user)
    return {"my": my_project_list, "join": join_project_list, "request": request}


@register.inclusion_tag("inclousion/manage_menu_list.html")
def manage_menu_list(request):
    data_list = [
        {"title": "概览", "url": reverse('web:dashboard', kwargs={"project_id": request.tracer.project.id})},
        {"title": "问题", "url": reverse('web:issues', kwargs={"project_id": request.tracer.project.id})},
        {"title": "统计", "url": reverse('web:statistics', kwargs={"project_id": request.tracer.project.id})},
        {"title": "wiki", "url": reverse('web:wiki', kwargs={"project_id": request.tracer.project.id})},
        {"title": "文件", "url": reverse('web:file', kwargs={"project_id": request.tracer.project.id})},
        {"title": "设置", "url": reverse('web:setting', kwargs={"project_id": request.tracer.project.id})},
    ]

    for data in data_list:
        # 用户当前访问的url是否以data_list里的一个url开头
        if request.path_info.startswith(data['url']):
            data["class"] = "active"

    return {"data_list": data_list}
