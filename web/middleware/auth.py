import datetime
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.conf import settings
from web import models


class Tracer(object):

    def __init__(self):
        self.user = None
        self.price_policy = None


class AuthMiddleware(MiddlewareMixin):

    def process_request(self, request):
        tracer = Tracer()

        user_id = request.session.get('user_id', 0)
        user_obj = models.UserInfo.objects.filter(id=user_id).first()
        # request.tracer = user_obj
        tracer.user = user_obj
        request.tracer = tracer

        # 判断当前访问url是否在白名单中 在白名单，继续走视图函数
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return
        # 用户不存在，返回登录页面
        if not request.tracer:
            return redirect("web:login")

        # 将价格策略保存到request，方便日后获取
        current_datetime = datetime.datetime.now()
        # 拿到当前用户最新的交易记录
        _object = models.Transaction.objects.filter(user=user_obj, status=1).order_by('-id').first()
        # 判断交易记录是否过期
        if _object.end_datetime and _object.end_datetime < current_datetime:
            _object = models.Transaction.objects.filter(user=user_obj, status=1, price_policy__category=1).first()
        # request.price_policy = _object.price_policy
        tracer.price_policy = _object.price_policy
        request.tracer = tracer
        """ 
        此时request中存了两个变量： 
            1. request.tracer  2. request.price_policy 
            是否可以将这两个值封装到一个函数？
            于是 有了上边的Tracer类
            封装后：request.tracer.user & request.tracer.price_policy，日后读代码更容易理解
        """