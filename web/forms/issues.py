from django import forms
from web import models
from web.forms.bootstrap import BootstrapForm


class IssuesForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'create_datetime', 'latest_update_datetime', 'creator']
        widgets = {
            'assign': forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),
            'attention': forms.SelectMultiple(attrs={"class": "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            'parent': forms.Select(attrs={"class": "selectpicker", "data-live-search": "true"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化数据
        # 获取当前所有的问题类型
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=request.tracer.project).values_list("id", "title")

        # 获取当前项目所有的模块
        module_list = [("", "没有选中任何项")]
        module_obj_list = models.Module.objects.filter(project=request.tracer.project).values_list("id", "title")
        module_list.extend(module_obj_list)
        self.fields['module'].choices = module_list

        # 获取当前项目的所有指派者 (创建者 & 参与者)
        user_list = [(request.tracer.project.creator.id, request.tracer.project.creator.name)]
        projectuser_obj_list = models.ProjectUser.objects.filter(project=request.tracer.project).values_list("user_id", "user__name")
        user_list.extend(projectuser_obj_list)
        self.fields['assign'].choices = [("", "没有选中任何项")] + user_list
        self.fields['attention'].choices = user_list

        # 获取当前项目所有的父问题
        parent_list = [("", "没有选中任何项")]
        parent_obj_list = models.Issues.objects.filter(project=request.tracer.project).values_list('id', 'subject')
        parent_list.extend(parent_obj_list)
        self.fields['parent'].choices = parent_list