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
    # https://test-1300113042.cos.ap-beijing.myqcloud.com/f1.txt
    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)