'''用户账户相关功能 如：登陆 短信 注册 注销'''
from django.shortcuts import render
from web.forms.account import RegisterForm


def register(request):
    form = RegisterForm()
    return render(request, 'web/register.html', {"form": form})