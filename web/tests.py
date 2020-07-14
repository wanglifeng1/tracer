import os
import sys
import django


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tracer.settings")
django.setup()


from web import models
models.UserInfo.objects.create(name='lixian', email='321@qq.com', password='321321', mobile_phone=13822222222)