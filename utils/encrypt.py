from hashlib import md5
from django.conf import settings


def make_md5(str):

    hash_obj = md5(settings.SECRET_KEY.encode('utf-8'))
    hash_obj.update(str.encode('utf-8'))

    return hash_obj.hexdigest()