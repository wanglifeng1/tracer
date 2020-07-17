from django.conf.urls import url, include
from web.views import account, home, manage, promanage, wiki

urlpatterns = [
    # 登陆/注册
    url(r'^register/$', account.register, name='register'),
    url(r'^login/$', account.login, name='login'),
    url(r'^login/sms/$', account.login_sms, name='login_sms'),
    url(r'^logout/$', account.logout, name='logout'),
    url(r'^send/sms/$', account.send_sms, name='send_sms'),
    url(r'^imgcode/$', account.img_code, name='img_code'),

    url(r'^index/$', home.index, name='index'),

    # 项目列表
    url(r'^project/list/$', manage.project_list, name='project_list'),
    url(r'^project/star/(?P<project_type>\w+)/(?P<project_id>\d+)/$', manage.project_star, name='project_star'),
    url(r'^project/unstar/(?P<project_type>\w+)/(?P<project_id>\d+)/$', manage.project_unstar, name='project_unstar'),

    # 项目管理
    url(r'^manage/(?P<project_id>\d+)/', include([
        url(r'^dashboard/$', promanage.dashboard, name='dashboard'),
        url(r'^issues/$', promanage.issues, name='issues'),
        url(r'^statistics/$', promanage.statistics, name='statistics'),

        url(r'^wiki/$', wiki.wiki, name='wiki'),
        url(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        url(r'^wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),

        url(r'^file/$', promanage.file, name='file'),
        url(r'^setting/$', promanage.setting, name='setting'),
    ])),

]

app_name = 'web'
