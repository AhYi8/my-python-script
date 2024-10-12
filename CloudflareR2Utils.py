import boto3
from botocore.exceptions import ClientError
import time
import logging

# Configure logging
logging.basicConfig(
    filename='log.txt',  # Save logs to log.txt
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Error log for failed operations
error_logger = logging.getLogger('error_logger')
error_handler = logging.FileHandler('error.txt')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)


class CloudflareR2Utils:
    access_key = None
    secret_key = None
    endpoint_url = None
    bucket_name = None
    _client = None
    RETRY_LIMIT = 3  # Maximum number of retries

    @staticmethod
    def configure(access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        """Configure the R2 credentials and bucket details."""
        CloudflareR2Utils.access_key = access_key
        CloudflareR2Utils.secret_key = secret_key
        CloudflareR2Utils.endpoint_url = endpoint_url
        CloudflareR2Utils.bucket_name = bucket_name

    @staticmethod
    def _get_client():
        """Initialize the boto3 client if it hasn't been created yet."""
        if CloudflareR2Utils._client is None:
            if not all([CloudflareR2Utils.access_key, CloudflareR2Utils.secret_key, CloudflareR2Utils.endpoint_url, CloudflareR2Utils.bucket_name]):
                raise ValueError("Cloudflare R2 credentials and bucket name must be configured before using this utility.")
            session = boto3.Session(
                aws_access_key_id=CloudflareR2Utils.access_key,
                aws_secret_access_key=CloudflareR2Utils.secret_key,
            )
            CloudflareR2Utils._client = session.client(
                's3',
                endpoint_url=CloudflareR2Utils.endpoint_url
            )
        return CloudflareR2Utils._client

    @staticmethod
    def _retry(func):
        """Decorator to automatically retry a function in case of failure."""
        def wrapper(*args, **kwargs):
            for attempt in range(CloudflareR2Utils.RETRY_LIMIT):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    logging.error(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < CloudflareR2Utils.RETRY_LIMIT - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise e
        return wrapper

    @staticmethod
    @_retry
    def upload_to_r2(file_path: str, file_key: str) -> str:
        """
        Uploads an image to Cloudflare R2 storage.
        :param file_path: Local file path to the image.
        :param file_key: Key (name) to store the image under in R2.
        :return: URL to the uploaded image.
        """
        client = CloudflareR2Utils._get_client()

        try:
            with open(file_path, 'rb') as file_data:
                client.upload_fileobj(file_data, CloudflareR2Utils.bucket_name, file_key)
            
            custom_domain = "https://<your-custom-domain>"
            file_url = f"{custom_domain}/{file_key}"
            logging.info(f"Successfully uploaded {file_key} to R2.")
            return file_url
        except ClientError as e:
            logging.error(f"Failed to upload {file_path} to R2: {e}")
            error_logger.error(f"Failed to upload {file_key}: {e}")
            raise

    @staticmethod
    @_retry
    def delete_from_r2(file_key: str) -> None:
        """
        Deletes a single file from Cloudflare R2 storage.
        :param file_key: Key (name) of the file to delete from R2.
        """
        client = CloudflareR2Utils._get_client()

        try:
            client.delete_object(Bucket=CloudflareR2Utils.bucket_name, Key=file_key)
            logging.info(f"Successfully deleted {file_key} from R2.")
        except ClientError as e:
            logging.error(f"Failed to delete {file_key} from R2: {e}")
            error_logger.error(f"Failed to delete {file_key}: {e}")
            raise

    @staticmethod
    @_retry
    def batch_upload_to_r2(files: dict) -> None:
        """
        Uploads multiple files to Cloudflare R2 storage.
        :param files: Dictionary where keys are local file paths and values are corresponding R2 keys.
        """
        for file_path, file_key in files.items():
            try:
                CloudflareR2Utils.upload_to_r2(file_path, file_key)
            except Exception as e:
                logging.error(f"Batch upload failed for {file_key}: {e}")
                error_logger.error(f"Batch upload failed for {file_key}: {e}")

    @staticmethod
    @_retry
    def batch_delete_from_r2(file_keys: list) -> None:
        """
        Deletes multiple files from Cloudflare R2 storage.
        :param file_keys: List of file keys (names) to delete from R2.
        """
        client = CloudflareR2Utils._get_client()

        try:
            objects = [{'Key': key} for key in file_keys]
            response = client.delete_objects(Bucket=CloudflareR2Utils.bucket_name, Delete={'Objects': objects})
            deleted = response.get('Deleted', [])
            errors = response.get('Errors', [])

            for obj in deleted:
                logging.info(f"Successfully deleted {obj['Key']} from R2.")
            for error in errors:
                logging.error(f"Failed to delete {error['Key']} from R2: {error['Message']}")
                error_logger.error(f"Failed to delete {error['Key']}: {error['Message']}")
        except ClientError as e:
            logging.error(f"Batch delete failed: {e}")
            error_logger.error(f"Batch delete failed: {e}")
            raise


# Usage Example:
# First configure the credentials and bucket details
CloudflareR2Utils.configure(
    access_key="<your-access-key>",
    secret_key="<your-secret-key>",
    endpoint_url="https://<your-r2-endpoint>",
    bucket_name="<your-bucket-name>"
)

# Batch upload files to R2
try:
    files_to_upload = {
        'path/to/local/image1.jpg': 'images/image1.jpg',
        'path/to/local/image2.jpg': 'images/image2.jpg'
    }
    CloudflareR2Utils.batch_upload_to_r2(files_to_upload)
except Exception as e:
    logging.error(f"Error in batch upload: {e}")

# Batch delete multiple files from R2
try:
    CloudflareR2Utils.batch_delete_from_r2(['images/image1.jpg', 'images/image2.jpg'])
except Exception as e:
    logging.error(f"Error in batch delete: {e}")
