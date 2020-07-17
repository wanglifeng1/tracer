from django.db import models


class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=32, db_index=True)
    password = models.CharField(verbose_name="密码", max_length=32)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32)


class PricePolicy(models.Model):
    """ 价格策略表 """
    category_choice = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '其他'),
    )
    category = models.SmallIntegerField(verbose_name='收费类型', choices=category_choice, default=2)
    title = models.CharField(verbose_name="标题", max_length=32)
    price = models.PositiveIntegerField(verbose_name="价格")    # 正整数

    project_num = models.PositiveIntegerField(verbose_name="项目个数")
    project_member = models.PositiveIntegerField(verbose_name="项目成员")
    project_space = models.PositiveIntegerField(verbose_name="项目空间")
    project_size = models.PositiveIntegerField(verbose_name="单个文件大小")

    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Transaction(models.Model):
    """交易记录"""
    status_choice = (
        (1, '已支付'),
        (2, '未支付'),
    )

    status = models.SmallIntegerField(verbose_name="交易状态", choices=status_choice)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)

    user = models.ForeignKey(verbose_name="用户", to="UserInfo", on_delete=models.CASCADE)
    price_policy = models.ForeignKey(verbose_name="价格策略", to="PricePolicy", on_delete=models.CASCADE)
    count = models.IntegerField(verbose_name="数量（年）", help_text="0表示无限期")

    price = models.IntegerField(verbose_name="实际支付价格")

    start_datetime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Project(models.Model):
    """ 项目表 """
    COLOR_CHOICES = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )
    name = models.CharField(verbose_name="项目名称", max_length=32)
    color = models.SmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)
    desc = models.CharField(verbose_name="项目描述", max_length=255, null=True, blank=True)

    use_space = models.IntegerField(verbose_name="项目已使用空间", default=0)
    star = models.BooleanField(verbose_name="星标", default=False)

    creator = models.ForeignKey(verbose_name="创建者", to="UserInfo", on_delete=models.CASCADE)
    join_count = models.IntegerField(verbose_name="参与人数", default=1)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class ProjectUser(models.Model):
    """ 项目参与者 """
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="用户", to="UserInfo", on_delete=models.CASCADE)
    # invitee = models.ForeignKey(verbose_name="邀请者", to="UserInfo", on_delete=models.CASCADE)
    star = models.BooleanField(verbose_name="星标", default=False)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Wiki(models.Model):
    """ wiki文档库 """
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="标题", max_length=32)
    content = models.TextField(verbose_name="内容")

    parent = models.ForeignKey(verbose_name="父文章", to="self", null=True, blank=True, related_name="children", on_delete=models.CASCADE)

    def __str__(self):
        return self.title
