from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = 'AKIDxgBQO6wGrDMGtFGDAx0nK3wZz0yg5OM3'      # 替换为用户的 secretId
secret_key = 'e9vAHArIWs4d3KNh8ICOO6WcSDpOlrjN'      # 替换为用户的 secretKey
region = 'ap-beijing'     # 替换为用户的 Region

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
# 2. 获取客户端对象
client = CosS3Client(config)

print(client.__dict__)
# response = client.create_bucket(
#     Bucket='testa-1300113042',
#     ACL='public-read'
# )

