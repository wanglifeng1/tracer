from django.core.exceptions import ValidationError
from django import forms
from web import models
from web.forms.bootstrap import BootstrapForm


class FolderForm(BootstrapForm, forms.ModelForm):
    """ 文件夹form表单 """
    def __init__(self, request, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent = parent

    class Meta:
        model = models.FileRegister
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data['name']
        # 去数据库判断《当前目录》下《此文件夹》是否存在
        exists = models.FileRegister.objects.filter(name=name, project=self.request.tracer.project,
                                                    type=1, parent=self.parent).exists()
        if exists:
            raise ValidationError("文件夹名称已存在")

        return name
