from django.test import TestCase

# Create your tests here.

import redis
# from django_redis import get_redis_connection
#
#
# conn = get_redis_connection()
# conn.set('name', 'juan')
# res = conn.get('name')
# print(res)

conn = redis.Redis(host="172.16.177.132", port=6379, password="123456", encoding='utf-8')
conn.flushall()
conn.set('name', 'juan')
res = conn.get('name')
print(res)