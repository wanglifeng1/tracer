#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from web import models
from web.forms.account import RegisterForm, SmsForm, LoginSmsForm

''' 
用户账户相关功能 如：登陆 短信 注册 注销 
'''


def register(request):
    """ 注册 """
    if request.method == "GET":
        form = RegisterForm()
        return render(request, 'web/register.html', {"form": form})
    form = RegisterForm(data=request.POST)
    if form.is_valid():
        form.save()    # 保存到数据库
        return JsonResponse({"status": True, "res": "/web/login/sms/"})
    return JsonResponse({"status": False, "error": form.errors})


def send_sms(request):
    """ 短信验证码 """
    # 只对手机号进行校验： 手机号是否为空，格式是否正确
    form = SmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def login_sms(request):
    """ 短信登陆 """
    if request.method == "GET":
        form = LoginSmsForm()
        return render(request, 'web/login.html', {"form": form})
    print(request.POST)
    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        # 校验通过，用户名信息写到session
        mobile_phone = form.cleaned_data['mobile_phone']
        # 这里重复到数据库查询了，在LoginSmsForm中已经查询过一次了，可以在form校验时返回用户对象进行优化
        user_obj = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id'] = user_obj.id
        return JsonResponse({"status": True, "res": "/web/index/"})
    return JsonResponse({"status": False, "error": form.errors})