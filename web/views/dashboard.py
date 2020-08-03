import time
import datetime
import collections
from django.shortcuts import render
from django.db.models import Count
from django.http import JsonResponse
from web import models


def dashboard(request, project_id):
    """ 概览 """
    # 问题数据处理
    status_dic = collections.OrderedDict()
    for key, text in models.Issues.status_choices:
        # status_dic=[(1, {'text': '新建', 'count': 0}), (2, {'text': '处理中', 'count': 0}),]
        status_dic[key] = {'text': text, 'count': 0}
    status_list = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in status_list:  # item {'status': 1, 'ct': 3}
        status_dic[item['status']]['count'] = item['ct']

    # 项目成员处理
    user_list = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__name')

    # 最新的10个问题
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]
    context = {
        'status_dic': status_dic,
        'user_list': user_list,
        'top_ten': top_ten,
    }
    return render(request, 'web/dashboard.html', context)


def issues_chart(request, project_id):
    """ 问题chart """
    # 获取最近30天 项目的所有问题数量
    today = datetime.datetime.now().date()
    date_dic = collections.OrderedDict()
    """
    {
        '2020-1-1': [1596081574.3670154, 0],
        '2020-1-2': [1596081574.3670154, 0],
        '2020-1-3': [1596081574.3670154, 0],
    }
    """
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        date_dic[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    result = models.Issues.objects.filter(project_id=project_id,
                                          create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={"ct": "strftime('%%Y-%%m-%%d', web_issues.create_datetime)"}
    ).values('ct').annotate(cd=Count('id'))
    # result = [{'ct': '2020-07-24', 'cd': 5}, {'ct': '2020-07-28', 'cd': 1}]
    for item in result:
        date_dic[item['ct']][1] = item['cd']
    print(date_dic.values())
    return JsonResponse({"status": True, "data": list(date_dic.values())})
