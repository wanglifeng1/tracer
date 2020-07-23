from scripts import base
from web import models


exists = models.PricePolicy.objects.filter(category=1, title="个人免费版", price=0).exists()
if not exists:
    price_policy = models.PricePolicy.objects.create(
        category=1,
        title="个人免费版",
        price=0,
        project_num=3,
        project_member=2,
        project_space=20,
        project_size=5,
    )
