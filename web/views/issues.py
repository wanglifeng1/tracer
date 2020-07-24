from django.shortcuts import render
from web.forms.issues import IssuesForm


def issues(request, project_id):
    """ 问题列表 """
    if request.method == "GET":
        form = IssuesForm(request)
        return render(request, 'web/issues.html', {"form": form})
