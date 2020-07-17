from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from web.forms.wiki import WikiModelForm
from web import models


def wiki(request, project_id):
    """ wiki首页 """
    wiki_id = request.GET.get('wiki_id')
    # 判断wiki_id是否存在，并且是否是数字
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'web/wiki.html')
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'web/wiki.html', {"wiki_obj": wiki_obj})


def wiki_add(request, project_id):
    """ wiki添加 """
    if request.method == "GET":
        form = WikiModelForm(request)
        return render(request, 'web/wiki_add.html', {"form": form})

    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过，保存到数据库之前，还有一个必填字段，project
        form.instance.project = request.tracer.project
        form.save()
        url = reverse("web:wiki", kwargs={"project_id": project_id})
        return redirect(url)
    return render(request, "web/wiki_add.html", {"form": form})


def wiki_catalog(request, project_id):
    """ wiki目录展示 """
    # 获取当前项目的所有wiki
    wiki_obj = models.Wiki.objects.filter(project_id=project_id).values('id', 'title', 'parent')      # 用values生成字典格式，方便前端取值，valuse_list生成列表（里边套元组）
    return JsonResponse({"status": True, "wiki_list": list(wiki_obj)})

