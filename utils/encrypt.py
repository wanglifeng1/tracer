import uuid
from hashlib import md5
from django.conf import settings


def make_md5(string):

    hash_obj = md5(settings.SECRET_KEY.encode('utf-8'))
    hash_obj.update(string.encode('utf-8'))

    return hash_obj.hexdigest()


def uid(string):
    data = "{}-{}".format(str(uuid.uuid4()), string)
    return make_md5(data)
