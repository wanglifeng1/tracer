from django.shortcuts import render
from django.http import JsonResponse
from web.forms.project import ProjectForm


def project_list(request):
    """ 后台管理 """
    if request.method == "GET":
        form = ProjectForm(request)
        return render(request, "web/project_list.html", {"form": form})
    form = ProjectForm(request, data=request.POST)
    if form.is_valid():
        # 校验通过，保存到数据库之前，还有一个必填字段，在form表单校验时没有
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})
