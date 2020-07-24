from django.conf.urls import url, include
from web.views import account, home, manage, promanage, wiki, file, setting, issues

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

        url(r'^statistics/$', promanage.statistics, name='statistics'),

        url(r'^wiki/$', wiki.wiki, name='wiki'),
        url(r'^wiki/add/$', wiki.wiki_add, name='wiki_add'),
        url(r'^wiki/catalog/$', wiki.wiki_catalog, name='wiki_catalog'),
        url(r'^wiki/delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
        url(r'^wiki/edit/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        url(r'^wiki/upload/$', wiki.wiki_upload, name='wiki_upload'),

        url(r'^file/$', file.file, name='file'),
        url(r'^file/delete/$', file.file_delete, name='file_delete'),
        url(r'^file/post/$', file.file_post, name='file_post'),
        url(r'^file/download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),
        url(r'^cos/credential/$', file.cos_credential, name='cos_credential'),

        url(r'^setting/$', setting.setting, name='setting'),
        url(r'^setting/delete/$', setting.setting_delete, name='setting_delete'),

        url(r'^issues/$', issues.issues, name='issues'),
    ])),

]

app_name = 'web'
