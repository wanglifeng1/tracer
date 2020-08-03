#!/usr/bin/env python
# -*- coding:utf-8 -*-
import uuid
import datetime
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q
from web import models
from web.forms.account import RegisterForm, SmsForm, LoginSmsForm, LoginForm
from io import BytesIO
from utils.image.img_code import check_code
from scripts import base

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
        # 用户信息保存到数据库
        instance = form.save()

        # 价格策略
        price_policy = models.PricePolicy.objects.filter(category=1, title="个人免费版", price=0).first()

        # 创建交易记录
        models.Transaction.objects.create(
            status=1,
            order=uuid.uuid4(),
            user=instance,
            price_policy=price_policy,
            count=0,
            price=0,
            start_datetime=datetime.datetime.now()
        )
        return JsonResponse({"status": True, "res": "/web/index/"})
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
        return render(request, 'web/login_sms.html', {"form": form})

    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        # 校验通过，用户名信息写到session
        mobile_phone = form.cleaned_data['mobile_phone']
        # 这里重复到数据库查询了，在LoginSmsForm中已经查询过一次了，可以在form校验时返回用户对象进行优化
        user_obj = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id'] = user_obj.id
        request.session.set_expiry(60 * 60 * 24 * 14)
        return JsonResponse({"status": True, "res": "/web/index/"})
    return JsonResponse({"status": False, "error": form.errors})


def login(request):
    ''' 用户名密码登陆 '''
    if request.method == "GET":
        form = LoginForm(request)
        return render(request, 'web/login.html', {"form": form})
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        # 邮箱或者手机号登陆 或 用户名/密码登陆
        user_obj = models.UserInfo.objects.filter(Q(mobile_phone=username) | Q(email=username)).filter(password=password).first()
        if user_obj:
            request.session['user_id'] = user_obj.id
            request.session.set_expiry(60 * 60 * 24 * 14)
            return redirect('web:index')
        form.add_error("username", "用户名或密码错误")
    return render(request, 'web/login.html', {"form": form})


def img_code(request):
    img_obj, code = check_code()

    # 将code保存到session
    request.session['img_code'] = code
    request.session.set_expiry(60)  # 设置session过期时间60s

    # 图片对象保存到内存
    stream = BytesIO()
    img_obj.save(stream, 'png')

    return HttpResponse(stream.getvalue())


def logout(request):
    request.session.flush()
    return redirect('web:index')
