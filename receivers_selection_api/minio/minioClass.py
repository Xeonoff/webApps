from minio import Minio
from minio.error import S3Error
from io import BytesIO
from base64 import b64encode, b64decode
import os
import pip._vendor.requests as requests
from datetime import timedelta
import io
from .minio_config import *

class MinioClass:
    def __init__(self):
        try:
            self.client = Minio(endpoint=ENDPOINT,
                                access_key=ACCESS_KEY,
                                secret_key=SECRET_KEY,
                                secure=False)
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def addUser(self, username: str):
        try:
            self.client.make_bucket(username)
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def removeUser(self, username: str):
        try:
            self.client.remove_bucket(username)
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def addImage(self, bucket: str, image_id: int, image_base64: str):
        try:
            image_stream = BytesIO(image_base64)
            self.client.put_object(bucket_name=bucket,
                                   object_name=f"{image_id}.jpg",
                                   data=image_stream,
                                   length=len(image_base64))
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def getImage(self, bucket: str, fine_title: str):
        try:
            result = self.client.get_presigned_url(
                method='GET',
                bucket_name=bucket,
                object_name=f"{fine_title}.jpg",
                expires=timedelta(minutes=1),
                )
            # print (result)
            return b64encode(BytesIO(result.data).read()).decode()
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def removeImage(self, bucket: str, title: str):
        try:
            self.client.remove_object(bucket_name=bucket,
                                      object_name=f"{title}.jpg")
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)