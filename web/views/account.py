#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
from django.conf import settings
from django.shortcuts import render, HttpResponse
from web.forms.account import RegisterForm
from web.utils.tencent import sms

''' 
用户账户相关功能 如：登陆 短信 注册 注销 
'''


def register(request):
    form = RegisterForm()
    return render(request, 'web/register.html', {"form": form})


def send_sms(request):
    print(request.GET)
    code = random.randrange(1000, 9999)
    res = sms.send_sms_single(settings.MOBILE_PHONE, settings.TEMPLATE_ID, [code, ])
    print(res)
    return HttpResponse('ok...')