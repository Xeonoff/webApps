from minio import Minio
from minio.error import S3Error
from io import BytesIO
from base64 import b64encode, b64decode
import os
import pip._vendor.requests as requests
from datetime import timedelta
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

    def addImage(self, username: str, image_id: int, image_base64: str):
        try:
            image_data = b64decode(image_base64)
            image_stream = BytesIO(image_data)
            self.client.put_object(bucket_name=username,
                                   object_name=f"{image_id}.jpg",
                                   data=image_stream,
                                   length=len(image_data))
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def getImage(self, username: str, image_id: int):
        try:
            return self.client.get_presigned_url(
                method='GET',
                bucket_name=username,
                object_name=f"{image_id}.jpg",
                expires=timedelta(minutes=1),
            )
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)

    def removeImage(self, username: str, image_id: int):
        try:
            self.client.remove_object(bucket_name=username,
                                      object_name=f"{image_id}.jpg")
        except S3Error as e:
            print("minio error occurred: ", e)
        except Exception as e:
            print("unexpected error: ", e)