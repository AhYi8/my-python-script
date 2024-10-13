import os, shutil, re, hashlib, boto3, time, logging, mysql.connector
from typing import List
from botocore.exceptions import ClientError
from mysql.connector import Error

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.getcwd(), 'file', 'log.txt'),  # Save logs to log.txt
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Error log for failed operations
error_logger = logging.getLogger('error_logger')
error_handler = logging.FileHandler(os.path.join(os.getcwd(), 'file', 'error.txt'))
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
error_logger.addHandler(error_handler)

class FileUtils:
    @staticmethod
    def copy_files_to_all_subdirs(files_to_copy: List[str], target_dir):
        """
        复制指定文件到指定文件夹及其子孙文件夹下
        :param files_to_copy:
        :param target_dir:
        :return:
        """
        # 遍历目标文件夹及其所有子文件夹
        for root, dirs, files in os.walk(target_dir):
            # 对每个子目录进行操作
            for file_path in files_to_copy:
                # 获取文件名
                file_name = os.path.basename(file_path)
                # 目标路径
                target_path = os.path.join(root, file_name)

                try:
                    # 复制文件
                    shutil.copy(file_path, target_path)
                    print(f"复制文件 {file_name} 到 {target_path}")
                except Exception as e:
                    print(f"复制文件失败 {file_name}: {e}")

    @staticmethod
    def list_files_in_directory(directory_path):
        try:
            # 列出目标文件夹中的所有项目
            items = os.listdir(directory_path)

            # 过滤出文件
            files = [item for item in items if os.path.isfile(os.path.join(directory_path, item))]
            files.sort()
            return files
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    @staticmethod
    def list_dirs_in_directory(directory_path):
        try:
            # 列出目标文件夹中的所有项目
            items = os.listdir(directory_path)

            # 过滤出文件
            dirs = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]

            return dirs
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def delete_files_with_keyword(directory: str, keyword: str):
        """
        递归删除指定目录及其子目录中包含特定关键字的文件.

        :param directory: 目标文件夹路径
        :param keyword: 要搜索的文件名关键字
        """
        for root, dirs, files in os.walk(directory):
            for file in files:
                if keyword in file:  # 检查文件名是否包含关键字
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except OSError as e:
                        print(f"Error deleting file {file_path}: {e}")

    def rename_images_in_subfolders(folder_path: str):
        # 遍历指定文件夹下的所有子文件夹
        for subdir in os.listdir(folder_path):
            subdir_path = os.path.join(folder_path, subdir)

            # 确保当前路径是一个子文件夹
            if os.path.isdir(subdir_path):
                # 获取子文件夹内的所有文件
                images = [f for f in os.listdir(subdir_path) if
                          f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]

                # 确定编号的位数，位数由图片的数量决定
                num_images = len(images)
                num_digits = len(str(num_images))  # 序号需要的位数

                # 遍历每个图片文件，重命名
                for idx, image in enumerate(images, start=1):
                    old_image_path = os.path.join(subdir_path, image)

                    # 构造新文件名：子文件夹名_序号.扩展名
                    new_image_name = f"{subdir}_{str(idx).zfill(num_digits)}{os.path.splitext(image)[1]}"
                    new_image_path = os.path.join(subdir_path, new_image_name)

                    # 重命名文件
                    os.rename(old_image_path, new_image_path)
                    print(f"Renamed: {old_image_path} -> {new_image_path}")

    @staticmethod
    def read_file(path: str, is_strip: bool = False, mode: str = 'r', encoding: str = 'u8'):
        if path is not None and len(path.strip()) != 0 and os.path.exists(path):
            try:
                with open(path, mode=mode, encoding=encoding) as rf:
                    data_list = rf.readlines()
                if is_strip:
                    data_list = [data.strip() for data in data_list]
                return data_list
            except BaseException as e:
                print(f"FileUtils.read_file(): {e}")
                return None
        else:
            return None

    @staticmethod
    def write_file(path: str, data_list: List[str], mode: str = 'w', encoding: str = 'u8'):
        if path is not None and len(path.strip()) != 0:
            parent_path = os.path.split(path)[0]
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)
            try:
                write_list = []
                for data in data_list:
                    if not data.endswith("\n"):
                        data = data + '\n'
                    write_list.append(data)

                with open(path, mode=mode, encoding=encoding) as wf:
                    wf.writelines(write_list)
            except BaseException as e:
                print(f"FileUtils.read_file(): {e}")


class MysqlClientUtils:
    # 饿汉式单例 - 初始化时即创建数据库连接
    _connection = None
    _table_columns_cache = {}
    _checked_log_tables = set()  # 缓存已经检查过的日志表
    _enable_logging = False  # 默认不开启日志

    # 静态方法，直接初始化数据库连接（用户可在此修改自己的配置）
    @staticmethod
    def _initialize_connection(host='152.32.175.149', port=3306, user='21zys', password='Mh359687..', database='my_database'):
        try:
            if MysqlClientUtils._connection is None:
                MysqlClientUtils._connection = mysql.connector.connect(
                    host=host,  # 替换为你的host
                    port=port,  # 替换为你的端口
                    user=user,  # 替换为你的用户名
                    password=password,  # 替换为你的密码
                    database=database  # 替换为你的数据库名
                )
                if MysqlClientUtils._connection.is_connected():
                    print("Database connection established")
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    @staticmethod
    def _get_current_time():
        """获取当前时间的字符串，格式为 'YYYY-MM-DD HH:MM:SS'"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _get_table_columns(table_name: str) -> List[str]:
        """获取指定表的字段列表，并缓存结果以提高效率"""
        if table_name in MysqlClientUtils._table_columns_cache:
            return MysqlClientUtils._table_columns_cache[table_name]

        MysqlClientUtils._initialize_connection()
        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()
            query = f"""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE()
                """
            cursor.execute(query, (table_name,))
            columns = [row[0] for row in cursor.fetchall()]
            MysqlClientUtils._table_columns_cache[table_name] = columns  # 缓存列名
            return columns
        except Error as e:
            print(f"Error fetching table columns: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _create_log_table_if_not_exists(table_name: str):
        """如果日志表不存在，自动创建日志表"""
        log_table_name = f"{table_name}_log"

        if log_table_name in MysqlClientUtils._checked_log_tables:
            return  # 如果已经检查过该日志表，直接返回

        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()

            # 检查日志表是否存在
            check_query = """
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE()
                """
            cursor.execute(check_query, (log_table_name,))
            if cursor.fetchone()[0] == 0:  # 日志表不存在
                create_log_table_query = f"""
                    CREATE TABLE {log_table_name} (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        full_query TEXT NOT NULL,
                        affected_rows INT NOT NULL,
                        create_time VARCHAR(19) NOT NULL
                    );
                    """
                cursor.execute(create_log_table_query)
                MysqlClientUtils._connection.commit()
                print(f"Log table '{log_table_name}' created.")

            # 记录已检查过的日志表
            MysqlClientUtils._checked_log_tables.add(log_table_name)
        except Error as e:
            print(f"Error creating log table {log_table_name}: {e}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _log_operation(table_name: str, full_query: str, affected_rows: int):
        """将完整SQL操作记录到 {table_name}_log 表"""
        MysqlClientUtils._create_log_table_if_not_exists(table_name)  # 自动创建日志表（如果不存在）

        log_table_name = f"{table_name}_log"
        log_query = f"""
            INSERT INTO {log_table_name} (full_query, affected_rows, create_time) 
            VALUES (%s, %s, %s)
            """
        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()
            current_time = MysqlClientUtils._get_current_time()  # 获取当前时间作为日志时间
            cursor.execute(log_query, (full_query, affected_rows, current_time))
            MysqlClientUtils._connection.commit()
        except Error as e:
            print(f"Error logging operation to {log_table_name}: {e}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _format_query(query: str, params: tuple) -> str:
        """将 SQL 语句与参数拼接成完整的 SQL 字符串"""
        try:
            return f"""{query % tuple(f"'{param}'" if isinstance(param, str) else param for param in params)};"""
        except Exception as e:
            print(f"Error formatting SQL query: {e}")
            return query  # 如果格式化失败，返回原始查询

    @staticmethod
    def _execute_with_retries(func, max_retries=3, retry_delay=2, *args, **kwargs):
        """通用重试机制，处理数据库操作"""
        attempt = 0
        while attempt < max_retries:
            try:
                return func(*args, **kwargs)
            except Error as e:
                print(f"Error during database operation: {e}")
                attempt += 1
                if attempt < max_retries:
                    print(f"Retrying ({attempt}/{max_retries}) in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Max retries reached. Operation failed.")
                    raise

    @staticmethod
    def enable_log():
        MysqlClientUtils._enable_logging = True

    @staticmethod
    def change_database(database_name: str):
        """切换当前数据库"""
        cursor = None
        try:
            MysqlClientUtils._initialize_connection()
            cursor = MysqlClientUtils._connection.cursor()
            cursor.execute(f"USE {database_name}")
            print(f"Switched to database: {database_name}")
        except Error as e:
            print(f"Error switching database: {e}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def initialize_client(host: str, port: int, user: str, password: str, database: str):
        """显式初始化数据库"""
        if MysqlClientUtils._connection is not None:
            MysqlClientUtils._connection.close()
            MysqlClientUtils._connection = None
        MysqlClientUtils._initialize_connection(host, port, user, password, database)


    # 执行INSERT操作
    @staticmethod
    def insert(table_name: str, params: Dict[str, any], auto_fill_timestamps: bool = False, max_retries=3, retry_delay=2):
        """插入单条数据，带重试机制"""
        MysqlClientUtils._initialize_connection()

        # 自动填充 create_time 和 update_time
        if auto_fill_timestamps:
            current_time = MysqlClientUtils._get_current_time()
            if 'create_time' not in params:
                params['create_time'] = current_time
            if 'update_time' not in params:
                params['update_time'] = current_time

        # 检查字段是否与表结构匹配
        valid_columns = MysqlClientUtils._get_table_columns(table_name)
        invalid_columns = [key for key in params.keys() if key not in valid_columns]
        if invalid_columns:
            raise ValueError(f"Invalid columns for table {table_name}: {invalid_columns}")

        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()
            first_row_fields = set(params.keys())
            # 生成插入字段和对应的占位符
            fields = ', '.join(first_row_fields)
            values_template = ', '.join(['%s'] * len(params))

            # 准备SQL语句
            query = f"INSERT INTO {table_name} ({fields}) VALUES ({values_template})"

            # 将字典的值转换为元组
            values = tuple(params[field] for field in first_row_fields)

            # 执行插入操作，使用重试机制
            def execute_insert():
                cursor.execute(query, values)
                MysqlClientUtils._connection.commit()
                return cursor.rowcount, cursor.lastrowid

            affected_rows, last_insert_id = MysqlClientUtils._execute_with_retries(execute_insert, max_retries,
                                                                                   retry_delay)

            # 记录完整的 SQL 语句到日志
            if MysqlClientUtils._enable_logging:
                full_query = MysqlClientUtils._format_query(query, values)
                MysqlClientUtils._log_operation(table_name, full_query, affected_rows)

            return last_insert_id  # 返回插入行的ID
        except Error as e:
            print(f"Error executing INSERT query: {e}")
            MysqlClientUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def bulk_insert(table: str, data: List[Dict[str, any]], auto_fill_timestamps: bool = False, max_retries=3,
                    retry_delay=2):
        """批量插入数据，带重试机制"""
        MysqlClientUtils._initialize_connection()

        if not data:
            raise ValueError("Data list is empty")
        if not isinstance(data, List):
            raise ValueError("Data is not a List")
        # 如果自动填充时间戳，检查并填充create_time和update_time字段
        if auto_fill_timestamps:
            current_time = MysqlClientUtils._get_current_time()
            for row in data:
                if 'create_time' not in row:
                    row['create_time'] = current_time
                if 'update_time' not in row:
                    row['update_time'] = current_time

        # 验证所有字典的字段是否一致
        first_row_fields = set(data[0].keys())
        for row in data:
            if set(row.keys()) != first_row_fields:
                raise ValueError("Inconsistent fields in input data")

        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()

            # 获取字段列表和对应的值占位符
            fields = ', '.join(first_row_fields)
            values_template = ', '.join(['%s'] * len(first_row_fields))

            # 准备SQL语句
            query = f"INSERT INTO {table} ({fields}) VALUES ({values_template})"

            # 将字典中的值转化为元组列表
            def prepare_row(row):
                return tuple(row[field] for field in first_row_fields)

            values = [prepare_row(row) for row in data]

            # 批量插入操作，使用重试机制
            def execute_bulk_insert():
                cursor.executemany(query, values)
                MysqlClientUtils._connection.commit()
                return cursor.rowcount

            affected_rows = MysqlClientUtils._execute_with_retries(execute_bulk_insert, max_retries, retry_delay)

            # 记录完整的 SQL 语句到日志
            if MysqlClientUtils._enable_logging:
                values = [f"""({','.join([f"'{row[field]}'" for field in first_row_fields])})""" for row in data]
                full_query = f"""INSERT INTO {table} ({fields}) VALUES {','.join(values)};"""
                MysqlClientUtils._log_operation(table, full_query, affected_rows)

            return affected_rows  # 返回插入的行数
        except Error as e:
            print(f"Error executing BULK INSERT query: {e}")
            MysqlClientUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def update(query: str, params: tuple, auto_update_timestamp: bool = False, max_retries=3, retry_delay=2):
        """更新数据，带重试机制"""
        MysqlClientUtils._initialize_connection()

        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()
            if auto_update_timestamp:
                # 如果需要自动更新 update_time 字段，添加到 SQL 和参数中
                current_time = MysqlClientUtils._get_current_time()
                query = query.replace("SET", "SET update_time = %s,", 1)  # 在 SET 后插入 update_time 字段
                params = (current_time,) + params  # 将当前时间插入参数前面

            # 执行更新操作，使用重试机制
            def execute_update():
                cursor.execute(query, params)
                MysqlClientUtils._connection.commit()
                return cursor.rowcount

            affected_rows = MysqlClientUtils._execute_with_retries(execute_update, max_retries, retry_delay)

            # 记录完整的 SQL 语句到日志
            if MysqlClientUtils._enable_logging:
                full_query = MysqlClientUtils._format_query(query, params)
                MysqlClientUtils._log_operation(query.split()[1], full_query, affected_rows)

            return affected_rows
        except Error as e:
            print(f"Error executing UPDATE query: {e}")
            MysqlClientUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    # 执行DELETE操作
    @staticmethod
    def delete(query, params):
        MysqlClientUtils._initialize_connection()
        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor()
            cursor.execute(query, params)
            MysqlClientUtils._connection.commit()
            return cursor.rowcount  # 返回受影响的行数
        except Error as e:
            print(f"Error executing DELETE query: {e}")
            MysqlClientUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    # 执行SELECT查询
    @staticmethod
    def select(query, params=None):
        MysqlClientUtils._initialize_connection()
        cursor = None
        try:
            cursor = MysqlClientUtils._connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"Error executing SELECT query: {e}")
        finally:
            if cursor:
                cursor.close()


class CloudflareR2Utils:
    access_key = "4d18ca2d2ed4f32b5fe0297961a908b8"
    secret_key = "660d2673568b4c7af0b73573683c5d9f5db136bb2b630a778995b8223e08bc67"
    endpoint_url = "https://5c01bbb3be6e040cd6fe7b91bdc4911d.r2.cloudflarestorage.com"
    bucket_name = "coser-img"
    custom_domain = "https://coser.21zys.top"
    _client = None
    RETRY_LIMIT = 3  # Maximum number of retries

    @staticmethod
    def configure(access_key: str="4d18ca2d2ed4f32b5fe0297961a908b8",
            secret_key: str="660d2673568b4c7af0b73573683c5d9f5db136bb2b630a778995b8223e08bc67",
            endpoint_url: str="https://5c01bbb3be6e040cd6fe7b91bdc4911d.r2.cloudflarestorage.com",
            bucket_name: str="coser-img",
            custom_domain: str = "https://coser.21zys.top"):
        """Configure the R2 credentials and bucket details."""
        CloudflareR2Utils.access_key = access_key
        CloudflareR2Utils.secret_key = secret_key
        CloudflareR2Utils.endpoint_url = endpoint_url
        CloudflareR2Utils.bucket_name = bucket_name
        CloudflareR2Utils.custom_domain = custom_domain

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

            file_url = f"{CloudflareR2Utils.custom_domain}/{file_key}"
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
    def batch_upload_to_r2(files: dict) -> list:
        """
        Uploads multiple files to Cloudflare R2 storage.
        :param files: Dictionary where keys are local file paths and values are corresponding R2 keys.
        """
        image_list = []
        for file_path, file_key in files.items():
            try:
                file_url = CloudflareR2Utils.upload_to_r2(file_path, file_key)
                image_list.append((file_path, file_key, file_url))
            except Exception as e:
                logging.error(f"Batch upload failed for {file_key}: {e}")
                error_logger.error(f"Batch upload failed for {file_key}: {e}")
        return image_list

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

    @staticmethod
    def uplaod_coser_images_to_r2(directory_path: str):
        sub_dir_list = FileUtils.list_dirs_in_directory(directory_path)
        for sub_dir in sub_dir_list:
            for file in FileUtils.list_files_in_directory(os.path.join(directory_path, sub_dir)):
                file_path = os.path.join(directory_path, sub_dir, file)
                file_key = f"{directory_path}/{sub_dir}/{file}"
                file_url = CloudflareR2Utils.upload_to_r2(file_path, file_key)
                print(f"{file_path} uploaded to R2 with URL: {file_url}")

    @staticmethod
    def generate_md5_hash(input_string):
        """
        生成给定字符串的MD5哈希值。

        参数:
        input_string (str): 需要被哈希的字符串。

        返回:
        str: 字符串的MD5哈希值。
        """
        if not isinstance(input_string, str):
            raise ValueError("输入必须是字符串类型")

        # 创建md5对象
        m = hashlib.md5()
        # 更新md5对象以添加字符串的字节表示形式
        m.update(input_string.encode('utf-8'))
        # 获取16进制的哈希值
        return m.hexdigest()

# Usage Example:
# First configure the credentials and bucket details
CloudflareR2Utils.configure()

if __name__ == "__main__":
    CloudflareR2Utils.uplaod_coser_images_to_r2(r"D:\BaiduNetdiskDownload\玉汇_images")


# Batch upload files to R2
# try:
#     files_to_upload = {
#         r'D:\ProgramFiles\Code\python\study\my-python-script\image\0-100人电商管理视频课程.jpg': 'test.jpg'
#     }
#     CloudflareR2Utils.batch_upload_to_r2(files_to_upload)
# except Exception as e:
#     logging.error(f"Error in batch upload: {e}")

# Batch delete multiple files from R2
# try:
#     CloudflareR2Utils.batch_delete_from_r2(['test.jpg'])
# except Exception as e:
#     logging.error(f"Error in batch delete: {e}")
