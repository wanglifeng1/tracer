from django.conf.urls import url
from web.views import account, home, manage

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
    url(r'^login/$', account.login, name='login'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^imgcode/$', account.img_code, name='img_code'),

    url(r'^index/$', home.index, name='index'),

    url(r'^project/list/$', manage.project_list, name='project_list'),

]

app_name = 'web'
