from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.forms.wiki import WikiModelForm
from utils import encrypt
from web import models
from web.utils.tencent.cos import cos_upload


def wiki(request, project_id):
    """ wiki首页 """
    wiki_id = request.GET.get('wiki_id')
    # 判断wiki_id是否存在，并且是否是数字
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'web/wiki.html')
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    return render(request, 'web/wiki.html', {"wiki_obj": wiki_obj})


def wiki_add(request, project_id):
    """ wiki添加 """
    if request.method == "GET":
        form = WikiModelForm(request)
        return render(request, 'web/wiki_form.html', {"form": form})

    form = WikiModelForm(request, data=request.POST)
    if form.is_valid():
        # 判断父文章是否为null
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        else:
            form.instance.depth = 1
        # 校验通过，保存到数据库之前，还有一个必填字段，project
        form.instance.project = request.tracer.project
        form.save()
        url = reverse("web:wiki", kwargs={"project_id": project_id})
        return redirect(url)
    return render(request, "web/wiki_form.html", {"form": form})


def wiki_catalog(request, project_id):
    """ wiki目录展示 """
    # 获取当前项目的所有wiki
    wiki_obj = models.Wiki.objects.filter(project_id=project_id).values('id', 'title', 'parent').order_by('depth', 'id')     # 用values生成字典格式，方便前端取值，valuse_list生成列表（里边套元组）
    return JsonResponse({"status": True, "wiki_list": list(wiki_obj)})


def wiki_delete(request, project_id, wiki_id):
    """ wiki删除一篇文章 """
    models.Wiki.objects.filter(id=wiki_id, project_id=project_id).delete()
    url = reverse('web:wiki', kwargs={"project_id": project_id})
    return redirect(url)


def wiki_edit(request, project_id, wiki_id):
    """ 编辑wiki文章 """
    wiki_obj = models.Wiki.objects.filter(id=wiki_id, project_id=project_id).first()
    if not wiki_obj:
        url = reverse("web:wiki", kwargs={"project_id": project_id})
        return redirect(url)
    if request.method == "GET":
        form = WikiModelForm(request, instance=wiki_obj)
        return render(request, 'web/wiki_form.html', {"form": form})
    form = WikiModelForm(request, data=request.POST, instance=wiki_obj)
    if form.is_valid():
        form.save()
        url = reverse("web:wiki", kwargs={"project_id": project_id})
        edit_url = "{}?wiki_id={}".format(url, wiki_id)
        return redirect(edit_url)
    return render(request, 'web/wiki_form.html', {"form": form})


@csrf_exempt
def wiki_upload(request, project_id):
    """" markdown上传图片 """
    result = {
        'success': 0,
        'message': None,
        'url': None
    }
    # 获取markdown要上传的图片对象
    img_obj = request.FILES.get('editormd-image-file')
    if not img_obj:
        result['message'] = "选择的对象不存在"
        return JsonResponse(result)
    ext = img_obj.name.rsplit('.')[-1]
    key = "{}.{}".format(encrypt.uid(request.tracer.user.mobile_phone), ext)
    # 调用上传图片函数，返回上传成功后cos查看图片的url
    img_url = cos_upload(
        bucket=request.tracer.project.bucket,
        region=request.tracer.project.region,
        file_obj=img_obj,
        key=key
    )
    result['success'] = 1
    result['url'] = img_url
    # response.setHeader("X-Frame-Options", "SAMEORIGIN"); // 解决IFrame拒绝的问题
    return JsonResponse(result)
