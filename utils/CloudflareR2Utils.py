"""Cloudflare R2 上传脚本"""
import os, boto3, time
from botocore.exceptions import ClientError
from .FileUtils import FileUtils
from .LogUtils import LogUtils



class CloudflareR2Utils:
    access_key = "16a00e2327b20636fe17bdd69faa7e7e"
    secret_key = "f239672ac8a5675e76dfbf8371b707db995ec591e848ca53d771535b934b62b2"
    endpoint_url = "https://5c01bbb3be6e040cd6fe7b91bdc4911d.r2.cloudflarestorage.com"
    api_token = "BD8NNBDypJVK2LUmLxk53O-qriGOS9ycf4JX5hgB"
    bucket_name = "coser-img"
    custom_domain = "https://coser.21zys.top"
    client = None
    retry_limit = 3  # Maximum number of retries

    @classmethod
    def configure(cls,
                  access_key: str="16a00e2327b20636fe17bdd69faa7e7e",
                  secret_key: str="f239672ac8a5675e76dfbf8371b707db995ec591e848ca53d771535b934b62b2",
                  endpoint_url: str="https://5c01bbb3be6e040cd6fe7b91bdc4911d.r2.cloudflarestorage.com",
                  bucket_name: str="coser-img",
                  custom_domain: str = "https://coser.21zys.top"):
        """
        配置R2凭据和bucket详细信息。
        :param access_key: 访问密钥 ID
        :param secret_key: 机密访问密钥
        :param endpoint_url: 为 S3 客户端使用管辖权地特定的终结点
        :param bucket_name: 存储桶名称
        :param custom_domain: 自定义域
        :return:
        """
        cls.access_key = access_key
        cls.secret_key = secret_key
        cls.endpoint_url = endpoint_url
        cls.bucket_name = bucket_name
        cls.custom_domain = custom_domain
        cls.client = cls.get_client()

    @classmethod
    def get_client(cls):
        """初始化客户端"""
        if cls.client is None:
            if not all([cls.access_key, cls.secret_key, cls.endpoint_url, cls.bucket_name]):
                raise ValueError("Cloudflare R2 credentials and bucket name must be configured before using this utility.")
            session = boto3.Session(
                aws_access_key_id=cls.access_key,
                aws_secret_access_key=cls.secret_key,
            )
            cls.client = session.client(
                's3',
                endpoint_url=cls.endpoint_url
            )
        return cls.client

    @classmethod
    def __retry(cls, func):
        """装饰器用于在失败情况下自动重试函数。"""
        def wrapper(*args, **kwargs):
            for attempt in range(cls.retry_limit):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    LogUtils.error(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < cls.retry_limit - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise e
        return wrapper

    @classmethod
    @__retry
    def upload_to_r2(cls, file_path: str, file_key: str) -> str:
        """
        将图像上传到 Cloudflare R2 存储。
        :param file_path: 图像的本地文件路径。
        :param file_key: 用于在 R2 中存储图像的键（名称）。
        :return: 上传图像的 URL。
"""
        client = cls.get_client()

        try:
            with open(file_path, 'rb') as file_data:
                client.upload_fileobj(file_data, cls.bucket_name, file_key)

            file_url = f"{cls.custom_domain}/{file_key}"
            LogUtils.info(f"Successfully uploaded {file_key} to R2.")
            return file_url
        except ClientError as e:
            LogUtils.error(f"Failed to upload {file_path} to R2: {e}")
            raise

    @classmethod
    @__retry
    def delete_from_r2(cls, file_key: str) -> None:
        """
        从 Cloudflare R2 存储中删除单个文件。
        :param file_key: 要从 R2 中删除的文件的键（名称）。
"""
        client = cls.get_client()

        try:
            client.delete_object(Bucket=cls.bucket_name, Key=file_key)
            LogUtils.info(f"Successfully deleted {file_key} from R2.")
        except ClientError as e:
            LogUtils.error(f"Failed to delete {file_key} from R2: {e}")
            raise

    @classmethod
    @__retry
    def batch_upload_to_r2(cls, files: dict) -> list:
        """
        将多个文件上传到 Cloudflare R2 存储。
        :param files: 字典，其中键是本地文件路径，值是相应的 R2 键。
        :return: 图像链接数组
        """
        image_list = []
        for file_path, file_key in files.items():
            try:
                file_url = cls.upload_to_r2(file_path, file_key)
                image_list.append((file_path, file_key, file_url))
            except Exception as e:
                LogUtils.error(f"Batch upload failed for {file_key}: {e}")
        return image_list

    @classmethod
    @__retry
    def batch_delete_from_r2(cls, file_keys: list) -> None:
        """
        从 Cloudflare R2 存储中删除多个文件。
        :param file_keys: 要从 R2 删除的文件键（名称）列表。
        """
        client = cls.get_client()

        try:
            objects = [{'Key': key} for key in file_keys]
            response = client.delete_objects(Bucket=cls.bucket_name, Delete={'Objects': objects})
            deleted = response.get('Deleted', [])
            errors = response.get('Errors', [])

            for obj in deleted:
                LogUtils.info(f"Successfully deleted {obj['Key']} from R2.")
            for error in errors:
                LogUtils.error(f"Failed to delete {error['Key']} from R2: {error['Message']}")
        except ClientError as e:
            LogUtils.error(f"Batch delete failed: {e}")
            raise

    @classmethod
    def uplaod_coser_images_to_r2(cls, directory_path: str):
        sub_dir_list = FileUtils.list_dirs_in_directory(directory_path)
        for sub_dir in sub_dir_list:
            for file in FileUtils.list_files_in_directory(os.path.join(directory_path, sub_dir)):
                file_path = os.path.join(directory_path, sub_dir, file)
                file_key = f"{directory_path}/{sub_dir}/{file}"
                file_url = cls.upload_to_r2(file_path, file_key)
                print(f"{file_path} uploaded to R2 with URL: {file_url}")


if __name__ == "__main__":
    CloudflareR2Utils.uplaod_coser_images_to_r2(r"D:\BaiduNetdiskDownload\玉汇_images")