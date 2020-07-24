from django.conf import settings

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


def create_bucket(bucket, region):
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'      # private  /  public-read / public-read-write
    )
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': '*',
                'ExposeHeader': '*',
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def cos_upload(bucket, region, file_obj, key):
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_obj,
        Key=key,
    )
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)


def cos_delete(bucket, region, key):
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    client.delete_object(
        Bucket=bucket,
        Key=key,
    )


def cos_deletes(bucket, region, key_list):
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects,
    )


def credential(bucket, region):
    """ 获取cos上传临时凭证 """
    from sts.sts import Sts
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]
    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 10,
        # 固定密钥 id
        'secret_id': secret_id,
        # 固定密钥 key
        'secret_key': secret_key,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict


def cos_check(bucket, region, key):
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    result = client.head_object(
        Bucket=bucket,
        Key=key,
    )
    return result


def delete_bucket(bucket, region):
    secret_id = settings.TENCENT_COS_SECRET_ID[0]
    secret_key = settings.TENCENT_COS_SECRET_KEY[0]

    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    # 删除桶中所有文件
    # 删除桶中所有碎片
    # 删除桶

    # 找到文件 删除
    part_objs = client.list_objects(bucket)
    print(part_objs)
    # 找到碎片 删除

