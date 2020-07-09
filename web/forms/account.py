from web import models
from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator


class RegisterForm(ModelForm):
    password = forms.CharField(label="密码", widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入密码"}))
    confirm_password = forms.CharField(label="重复密码", widget=forms.PasswordInput())
    mobile_phone = forms.CharField(label="手机号", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', "手机号格式错误")])
    code = forms.CharField(label="验证码")

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "confirm_password", "email", "mobile_phone", "code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["placeholder"] = "请输入{}".format(field.label)