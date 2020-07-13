import random
from web import models
from django_redis import get_redis_connection
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from web.utils.tencent import sms
from .bootstrap import BootstrapForm
from utils.encrypt import make_md5


class RegisterForm(BootstrapForm, forms.ModelForm):
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(),
        min_length=8,
        max_length=32,
        error_messages={
            'min_length': '密码不能少于8位',
            'max_length': '密码最长不超过32位',
        }
    )
    confirm_password = forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput(),
        min_length=8,
        max_length=32,
        error_messages={
            'min_length': '确认密码不能少于8位',
            'max_length': '确认密码最长不超过32位',
        }
    )
    mobile_phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', "手机号格式错误")]
    )
    code = forms.CharField(label="验证码")

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "confirm_password", "email", "mobile_phone", "code"]

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exsits = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exsits:
            raise ValidationError("手机号已存在")
        return mobile_phone

    def clean_password(self):
        password = self.cleaned_data['password']
        if not password:
            raise ValidationError("密码不能为空")
        # 加密 & 保存
        return make_md5(password)

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = make_md5(self.cleaned_data['confirm_password'])
        if password != confirm_password:
            raise ValidationError("两次密码输入不一致，请重新输入")
        return confirm_password

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # 对照redis中code，校验是否一致
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)         # byte类型
        print(redis_code)
        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')
        str_code = redis_code.decode('utf-8')
        if code.strip() != str_code:
            raise ValidationError('验证码错误，请重新获取')
        return code


class LoginSmsForm(BootstrapForm, forms.Form):
    mobile_phone = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', "手机号格式错误")]
    )
    code = forms.CharField(label="验证码", widget=forms.TextInput())

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exsits = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if not exsits:
            raise ValidationError("手机号不存在")
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')

        if not mobile_phone:  # 手机号不存在，验证码无需校验
            return code

        # 对照redis中code，校验是否一致
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)  # byte类型
        print(redis_code)

        if not redis_code:
            raise ValidationError('验证码失效或未发送，请重新发送')
        str_code = redis_code.decode('utf-8')

        if code.strip() != str_code:
            raise ValidationError('验证码错误，请重新获取')
        return code


class SmsForm(forms.Form):
    mobile_phone = forms.CharField(label="手机号", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', "手机号格式错误")])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        ''' 手机号验证的钩子函数 '''
        mobile_phone = self.cleaned_data['mobile_phone']

        # 验证短信模板是否有效
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE[tpl]
        if not template_id:
            raise ValidationError("短信模板错误")

        # 验证手机号是否存在
        exist = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == "login":     # 登陆手机号校验
            if not exist:
                raise ValidationError("手机号不存在")

        else:                # 注册手机号校验
            if exist:
                raise ValidationError("手机号已经注册过")

        # 发送短信
        code = random.randrange(1000, 9999)
        res = sms.send_sms_single(mobile_phone, template_id, [code, ])
        if res['result'] != 0:
            raise ValidationError("发送短信失败：{}".format(res['errmsg']))

        # 验证码保存到redis
        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)

        return mobile_phone


class LoginForm(BootstrapForm, forms.Form):
    username = forms.CharField(label="手机号或邮箱")
    # username = forms.CharField(label="用户名")
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    code = forms.CharField(label="图片验证码")

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_password(self):
        password = self.cleaned_data.get('password')
        print("pwd: ", password)
        if not password:
            raise ValidationError("密码不能为空")
        # 加密 & 保存
        return make_md5(password)

    def clean_code(self):
        # 读取用户输入的验证码
        code = self.cleaned_data['code']
        # 去session中获取验证码
        session_code = self.request.session.get('img_code')
        print("session_code:", session_code)
        if not session_code:
            raise ValidationError("验证码已过期，请重新获取")
        if code.strip().upper() != session_code:
            raise ValidationError("验证码错误")
        return code
