import json
import datetime
from utils.encrypt import uid
from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from web import models
from web.forms.issues import IssuesForm, IssuesReplyModelForm, InviteForm
from web.utils.pagination import Pagination


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        self.data_list = data_list
        self.request = request
        self.name = name

    def __iter__(self):
        for item in self.data_list:
            ck = ''
            value_list = self.request.GET.getlist(self.name)
            if str(item[0]) in value_list:
                ck = "checked"
                value_list.remove(str(item[0]))
            else:
                value_list.append(str(item[0]))

            queryset_dict = self.request.GET.copy()
            queryset_dict._mutable = True
            queryset_dict.setlist(self.name, value_list)
            if "page" in queryset_dict:
                queryset_dict.pop('page')
            if queryset_dict.urlencode():
                url = "{}?{}".format(self.request.path_info, queryset_dict.urlencode())
            else:
                url = self.request.path_info
            tpl = "<a class='cell' href='{url}'><input type='checkbox' {ck} /><label> {text}</label></a>"
            html = tpl.format(url=url, ck=ck, text=item[1])
            yield mark_safe(html)


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width: 100%'>")
        for item in self.data_list:
            # item为一个个元组 (3, 'wanglifeng')
            value_list = self.request.GET.getlist(self.name)
            select = ''
            if str(item[0]) in value_list:
                select = "selected"
                value_list.remove(str(item[0]))
            else:
                value_list.append(str(item[0]))
            queryset_dict = self.request.GET.copy()
            queryset_dict._mutable = True
            queryset_dict.setlist(self.name, value_list)
            if "page" in queryset_dict:
                queryset_dict.pop('page')
            if queryset_dict.urlencode():
                url = "{}?{}".format(self.request.path_info, queryset_dict.urlencode())
            else:
                url = self.request.path_info
            tpl = "<option val='{url}' {selected}>{text}</option>"
            html = tpl.format(url=url, selected=select, text=item[1])
            yield mark_safe(html)
        yield mark_safe("</select>")


def issues(request, project_id):
    """ 问题列表 """
    # 筛选url处理
    allow_filter_list = ['priority', 'status', 'mode', 'issues_type', 'assign', 'attention']
    condition = {}
    for item in allow_filter_list:
        value_list = request.GET.getlist(item)
        if not value_list:
            continue
        condition["{}__in".format(item)] = value_list
    # condition = {'priority__in': ['danger'], 'status__in': ['1', '2'], 'mode__in': ['1']}

    queryset = models.Issues.objects.filter(project_id=project_id).filter(**condition)
    if request.method == "GET":
        page_obj = Pagination(
            current_page=request.GET.get('page'),
            all_count=queryset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=11
        )
        issues_list = queryset[page_obj.start: page_obj.end]
        form = IssuesForm(request)
        issues_type = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')
        # 项目创建者
        project_user_list = [(request.tracer.project.creator_id, request.tracer.project.creator.name)]
        # 项目参与者
        project_user = models.ProjectUser.objects.filter(project_id=project_id).values_list('user_id', 'user__name')
        project_user_list.extend(project_user)
        invite_form = InviteForm()
        context = {
            "form": form,
            "invite_form": invite_form,
            "issues_list": issues_list,
            "page_html": page_obj.page_html(),
            "filter": [
                {"name": "问题类型", "filter": CheckFilter('issues_type', issues_type, request)},
                {"name": "状态", "filter": CheckFilter('status', models.Issues.status_choices, request)},
                {"name": "优先级", "filter": CheckFilter('priority', models.Issues.priority_choices, request)},
                {"name": "模式", "filter": CheckFilter('mode', models.Issues.mode_choices, request)},
                {"name": "指派者", "filter": SelectFilter('assign', project_user_list, request)},
                {"name": "关注者", "filter": SelectFilter('attention', project_user_list, request)},
            ],
        }
        return render(request, 'web/issues.html', context)
    form = IssuesForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def issues_detail(request, project_id, issues_id):
    """ 问题编辑 """
    issues_obj = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    form = IssuesForm(request, instance=issues_obj)
    return render(request, "web/issues_detail.html", {"form": form, "issues_obj": issues_obj})


@csrf_exempt
def issues_record(request, project_id, issues_id):
    """ 问题记录 & 评论 """
    if request.method == "GET":
        reply_list = models.IssuesReply.objects.filter(issues_id=issues_id, issues__project=request.tracer.project)
        # queryset --> json
        data_list = []
        for row in reply_list:
            data = {
                "id": row.id,
                "reply_type": row.get_reply_type_display(),
                "content": row.content,
                "creator": row.creator.name,
                "create_datetime": row.create_datetime,
                "reply_id": row.reply_id
            }
            data_list.append(data)
        return JsonResponse({"status": True, "data": data_list})
    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.reply_type = 2
        form.instance.issues_id = issues_id
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            "id": instance.id,
            "reply_type": instance.get_reply_type_display(),
            "content": instance.content,
            "creator": instance.creator.name,
            "create_datetime": instance.create_datetime,
            "reply_id": instance.reply_id
        }
        return JsonResponse({"status": True, "data": info})
    return JsonResponse({"status": False, "error": form.errors})


@csrf_exempt
def issues_change(request, project_id, issues_id):
    """ 问题变更 """
    issues_obj = models.Issues.objects.filter(id=issues_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    name = post_dict.get('name')
    value = post_dict.get('value')
    field_obj = models.Issues._meta.get_field(name)

    def create_record(content):
        record_obj = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_obj,
            content=msg,
            creator=request.tracer.user,
        )
        data = {
            "id": record_obj.id,
            "reply_type": record_obj.get_reply_type_display(),
            "content": record_obj.content,
            "creator": record_obj.creator.name,
            "create_datetime": record_obj.create_datetime,
            "reply_id": record_obj.reply_id
        }
        return data
    # 1. 数据库更新
    # 1.1 文本
        # 保存前判断：1.该值是否为空
        #           2. 为空，为数据库比对，是否有null
    if name in ['subject', 'desc', 'start_date', 'end_date']:
        if value:
            setattr(issues_obj, name, value)
            issues_obj.save()
            msg = "{}变更为{}".format(field_obj.verbose_name, value)
        else:
            if not field_obj.null:
                return JsonResponse({"status": False, "error": "您选择的值不能为空"})
            setattr(issues_obj, name, None)
            issues_obj.save()
            msg = "{}变更为空".format(field_obj.verbose_name)
        return JsonResponse({"status": True, "data": create_record(msg)})
    # 1.2 FK
    if name in ['parent', 'issues_type', 'module', 'assign']:
        # 判断value是否为空
        if value:
            # 指派单独校验，不能为非法用户
            if name == "assign":
                # 判断是否是项目创建者
                if value == str(request.tracer.project.creator_id):
                    instance = request.tracer.project.creator
                else:
                    # 判断是否是项目参与者
                    project_user_obj = models.ProjectUser.objects.filter(user_id=value,project_id=project_id).first()
                    if project_user_obj:
                        instance = request.tracer.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({"status": False, "error": "您选择的值不正确"})
            else:
                instance = field_obj.rel.model.object.filter(id=value, project_id=project_id)
                if not instance:
                    return JsonResponse({"status": False, "error": "您选择的值不正确"})
            setattr(issues_obj, name, instance)
            issues_obj.save()
            msg = "{}变更为{}".format(field_obj.verbose_name, str(instance))
        else:  # value为空，则查看数据库该字段是否有null
            if not field_obj.null:
                return JsonResponse({"status": False, "error": "您选择的值不能为空"})
            setattr(issues_obj, name, None)
            issues_obj.save()
            msg = "{}变更为空".format(field_obj.verbose_name)
        return JsonResponse({"status": True, "data": create_record(msg)})

    # 1.3 choices
    if name in ['priority', 'status', 'mode']:
        select_text = None
        for item, text in field_obj.choices:
            if value == str(item):
                select_text = text
        if not select_text:
            return JsonResponse({'status': False, 'error': "您选择的值不存在"})
        setattr(issues_obj, name, value)
        issues_obj.save()
        msg = "{}变更为{}".format(field_obj.verbose_name, select_text)
        return JsonResponse({"status": True, "data": create_record(msg)})
    # 1.4 m2m
    if name == "attention":
        if not isinstance(value, list):
            return JsonResponse({"status": False, "error": "数据格式错误"})
        if not value:
            issues_obj.attention.set(value)
            issues_obj.save()
            msg = "{}变更为空".format(field_obj.verbose_name)
        else:
            # 获取项目的所有成员
            project_user_list = models.ProjectUser.objects.filter(project_id=project_id)
            user_dic = {str(request.tracer.project.creator_id): request.tracer.project.creator.name}
            for project_user in project_user_list:   # 循环数据库中该项目所有成员
                user_dic[str(project_user.user.id)] = project_user.user.name
            username_list = []
            for user_id in value:      # 循环用户选择的用户id
                username = user_dic.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在"})
                username_list.append(username)
            issues_obj.attention.set(value)
            issues_obj.save()
            msg = "{}变更为{}".format(field_obj.verbose_name, ','.join(username_list))
        return JsonResponse({"status": True, "data": create_record(msg)})
    # 2. 生成操作记录
    return JsonResponse({"status": False, "error": "滚"})


@csrf_exempt
def issues_invite(request, project_id):
    """ 生成邀请码 """
    form = InviteForm(data=request.POST)
    if form.is_valid():
        # 限制：只有创建者才能生成邀请码
        if request.tracer.user != request.tracer.project.creator:
            form.add_error('period', '只有项目创建者才可以生成邀请码')
            return JsonResponse({"status": False, "error": form.errors})
        invite_code = uid(request.tracer.user.mobile_phone)
        form.instance.project = request.tracer.project
        form.instance.code = invite_code
        form.instance.creator = request.tracer.user
        form.save()
        # 将验证码生成的url返回前端  拼接url
        url = "{scheme}://{host}{code}".format(
            scheme=request.scheme,
            host=request.get_host(),
            code=reverse('web:invite_join', kwargs={'code': invite_code})
        )
        return JsonResponse({"status": True, "data": url})

    return JsonResponse({"status": False, "error": form.errors})


def invite_join(request, code):
    """ 加入邀请 """
    invite_code_obj = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_code_obj:
        return render(request, 'web/invite_join.html', {'error': "您访问的邀请码不存在"})
    # 项目创建者?
    if invite_code_obj.project.creator == request.tracer.user:
        return render(request, 'web/invite_join.html', {'error': "创建者无需重复加入"})
    # 已经加入项目?
    exists = models.ProjectUser.objects.filter(project=invite_code_obj.project, user=request.tracer.user).exists()
    if exists:
        return render(request, 'web/invite_join.html', {'error': "您已经加入项目，无需在加入"})
    # 项目人数限制?
    # 1. 获取项目总成员
    # 2. 项目当前成员
    max_user = request.tracer.price_policy.project_member
    current_user = models.ProjectUser.objects.filter(project=invite_code_obj.project).count()
    if current_user + 1 >= max_user:
        return render(request, 'web/invite_join.html', {'error': "项目成员超限，请升级套餐"})

    # 邀请码过期?
    # 1. 当前时间
    # 2. 邀请码失效时间
    current_datetime = datetime.datetime.now()
    limit_datetime = invite_code_obj.create_datetime + datetime.timedelta(minutes=invite_code_obj.period)
    if current_datetime > limit_datetime:
        return render(request, 'web/invite_join.html', {'error': "邀请码已过期,请重新获取"})

    # 邀请码数量限制?
    if invite_code_obj.count:
        if invite_code_obj.use_count >= invite_code_obj.count:
            return render(request, 'web/invite_join.html', {'error': "邀请码数量超限"})
        invite_code_obj.use_count += 1
        invite_code_obj.save()

    # 没有数量限制
    models.ProjectUser.objects.create(user=request.tracer.user, project=invite_code_obj.project)
    return render(request, 'web/invite_join.html', {'project': invite_code_obj.project})