from django import forms
from web import models
from web.forms.widgets import ColorRadioSelect
from .bootstrap import BootstrapForm
from django.core.exceptions import ValidationError


class ProjectForm(BootstrapForm, forms.ModelForm):
    bootstrap_class_exclude = ['color']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = models.Project
        fields = ['name', 'color', 'desc']
        widgets = {
            'desc': forms.Textarea,
            'color': ColorRadioSelect(attrs={"class": "color-radio"}),  # 自定义组件
        }

    def clean_name(self):
        # 1. 该用户要创建的项目名称是否已经存在
        # 1.1 获取用户
        user_obj = self.request.tracer.user
        # 1.2 判断项目名是否已存在
        name = self.cleaned_data['name']
        exists = models.Project.objects.filter(creator=user_obj, name=name).exists()
        if exists:
            raise ValidationError("该项目已创建")
        # 2. 项目数量是否已达最大允许创建数
        # 2.1 获取用户最大项目个数
        project_num = self.request.tracer.price_policy.project_num
        # 2.2 查看当前已创建的项目个数
        count = models.Project.objects.filter(creator=user_obj).count()
        if count >= project_num:
            raise ValidationError("项目个数超限，请购买套餐")
        return name
