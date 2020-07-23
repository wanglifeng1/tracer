from django.core.exceptions import ValidationError
from django import forms
from web import models
from web.utils.tencent.cos import cos_check
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


class FileForm(forms.ModelForm):
    etag = forms.CharField(label="ETag")

    class Meta:
        model = models.FileRegister
        exclude = ["project", "type", "update_user", "update_time"]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_file_path(self):
        return "https://{}".format(self.cleaned_data['file_path'])

    def clean(self):
        key = self.cleaned_data['key']
        etag = self.cleaned_data['etag']
        file_size = self.cleaned_data['file_size']

        if not key or not etag:
            return self.cleaned_data
        # 向cos校验文件
        # SDK有个功能
        from qcloud_cos.cos_exception import CosServiceError
        try:
            res = cos_check(self.request.tracer.project.bucket, self.request.tracer.project.region, key)
        except CosServiceError as e:
            self.add_error("key", "文件不存在")
            return self.cleaned_data

        cos_etag = res['ETag']
        cos_size = res['Content-Length']
        # 前端发来的数据和cos数据校验
        if etag != cos_etag:
            self.add_error(etag, "ETag错误")
        if int(file_size) != int(cos_size):
            self.add_error(file_size, "文件大小错误")
        return self.cleaned_data
