from django import forms
from web import models
from web.forms.bootstrap import BootstrapForm


class WikiModelForm(BootstrapForm, forms.ModelForm):

    class Meta:
        model = models.Wiki
        exclude = ["project", "depth"]

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        total_data_list = [('', '请选择'), ]
        # 从数据库找到想要的字段，把他绑定显示的数据重置
        wiki_list = models.Wiki.objects.filter(project_id=request.tracer.project.id).values_list('id', 'title')
        total_data_list.extend(wiki_list)
        # 显示自己定义的parent字段
        self.fields['parent'].choices = total_data_list
