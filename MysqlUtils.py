import mysql.connector, time, os, phpserialize, re, redis, shutil
from typing import List, Dict
from mysql.connector import Error
from datetime import datetime

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

    # @staticmethod
    # def modify_all_files_properties_in_directory(directory: str, title: str, subject: str, tags: str, comments: str):
    #     try:
    #         # 使用DsoFile的COM对象
    #         dso = win32com.client.Dispatch("DSOFile.OleDocumentProperties")
    #
    #         for root, _, files in os.walk(directory):
    #             for file in files:
    #                 file_path = os.path.join(root, file)
    #
    #                 try:
    #                     # 打开文件以修改其属性
    #                     dso.Open(file_path)
    #
    #                     # 修改文件的摘要属性：标题、主题、标记、备注
    #                     dso.SummaryProperties.Title = title
    #                     dso.SummaryProperties.Subject = subject
    #                     dso.SummaryProperties.Keywords = tags
    #                     dso.SummaryProperties.Comments = comments
    #
    #                     # 保存修改
    #                     dso.Save()
    #                     print(f"已修改文件属性: {file_path}")
    #
    #                 except Exception as e:
    #                     print(f"修改文件属性时出错: {file_path}, 错误: {e}")
    #
    #         dso.Close()
    #
    #     except Exception as e:
    #         print(f"发生错误: {e}")

    @staticmethod
    def coser_picture_folders_rename(main_folder):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'}

        def get_readable_size(size_in_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_in_bytes < 1024:
                    return f"{size_in_bytes:.2f}{unit}"
                size_in_bytes /= 1024

        folder_list = [os.path.join(main_folder, folder) for folder in os.listdir(main_folder)
                       if os.path.isdir(os.path.join(main_folder, folder))]

        for folder in folder_list:
            page_total = 0
            video_total = 0
            total_size = 0

            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()

                    if file_ext in image_extensions:
                        page_total += 1
                    elif file_ext in video_extensions:
                        video_total += 1

                    total_size += os.path.getsize(file_path)

            size = get_readable_size(total_size)
            folder_name = os.path.basename(folder)
            new_stats = f"[{page_total}P" + (f"{video_total}V" if video_total != 0 else "") + f"-{size}]"
            new_folder_name = re.sub(r"\[\d+.*B]", new_stats, folder_name)
            new_folder_path = os.path.join(os.path.dirname(folder), new_folder_name)
            os.rename(folder, new_folder_path)
            print(f"Renamed '{folder}' to '{new_folder_path}'")

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


class RedisUtils:
    # Redis 连接属性，用户提供
    host = "152.32.175.149"
    port = 6379
    db = 0
    password = "Mh359687.."
    res_21zys_com_new_links = 'res_21zys_com_new_links'


    # 饿汉式初始化 Redis 客户端，确保客户端只初始化一次
    _redis_client = redis.StrictRedis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True
    )

    # ------------------ String 类型操作 ------------------
    @staticmethod
    def set_string(key: str, value: str):
        return RedisUtils._redis_client.set(key, value)

    @staticmethod
    def get_string(key: str):
        return RedisUtils._redis_client.get(key)

    @staticmethod
    def del_key(key: str):
        return RedisUtils._redis_client.delete(key)

    @staticmethod
    def update_string(key: str, value: str):
        return RedisUtils._redis_client.set(key, value)

    # ------------------ List 类型操作 ------------------
    @staticmethod
    def push_list(key: str, *values):
        return RedisUtils._redis_client.rpush(key, *values)

    @staticmethod
    def get_list(key: str, start: int = 0, end: int = -1):
        return RedisUtils._redis_client.lrange(key, start, end)

    @staticmethod
    def pop_list(key: str):
        return RedisUtils._redis_client.lpop(key)

    @staticmethod
    def list_length(key: str):
        return RedisUtils._redis_client.llen(key)

    # ------------------ Set 类型操作 ------------------
    @staticmethod
    def add_set(key: str, *values):
        return RedisUtils._redis_client.sadd(key, *values)

    @staticmethod
    def get_set(key: str):
        return RedisUtils._redis_client.smembers(key)

    @staticmethod
    def rem_set(key: str, *values):
        return RedisUtils._redis_client.srem(key, *values)

    @staticmethod
    def set_length(key: str):
        return RedisUtils._redis_client.scard(key)

    # ------------------ Hash 类型操作 ------------------
    @staticmethod
    def set_hash(key: str, field: str, value: str):
        return RedisUtils._redis_client.hset(key, field, value)

    @staticmethod
    def get_hash(key: str, field: str):
        return RedisUtils._redis_client.hget(key, field)

    @staticmethod
    def get_all_hash(key: str):
        return RedisUtils._redis_client.hgetall(key)

    @staticmethod
    def del_hash(key: str, field: str):
        return RedisUtils._redis_client.hdel(key, field)

    # ------------------ Zset 类型操作 ------------------
    @staticmethod
    def add_zset(key: str, score: float, value: str):
        return RedisUtils._redis_client.zadd(key, {value: score})

    @staticmethod
    def get_zset(key: str, start: int = 0, end: int = -1, withscores: bool = False):
        return RedisUtils._redis_client.zrange(key, start, end, withscores=withscores)

    @staticmethod
    def rem_zset(key: str, *values):
        return RedisUtils._redis_client.zrem(key, *values)

    @staticmethod
    def zset_length(key: str):
        return RedisUtils._redis_client.zcard(key)

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


def test_output_category_links():
    replaced_links = RedisUtils.get_set(RedisUtils.res_21zys_com_new_links)
    category = '图书小说'
    query = f"""
            select * from wp_postmeta
            where meta_key = 'cao_downurl_new' and post_id in (
                select object_id from `wp_term_relationships`
                where term_taxonomy_id in (
                    select t.term_id from `wp_terms` as t
                    inner join `wp_term_taxonomy` tt on t.term_id = tt.term_id
                    where t.name = '{category}' and tt.taxonomy = 'category'
                )
            );
        """
    MysqlClientUtils.change_database("res_21zys_com")
    result = MysqlClientUtils.select(query)
    urls = []
    for data in result:
        url = str(phpserialize.loads(bytes(data['meta_value'], encoding='UTF-8'))[0][b'url'], 'UTF-8')
        if 'pan.quark.cn' in url and url not in replaced_links:
            urls.append(url)
    FileUtils.write_file(r"C:\Users\Administrator\Desktop\old_urls.csv", urls)


def test_replace_new_links():
    replaced_links = RedisUtils.get_set(RedisUtils.res_21zys_com_new_links)
    new_urls = {}
    for url_map_list in FileUtils.read_file(r"C:\Users\Administrator\Desktop\new_urls.txt", is_strip=True):
        new_urls[url_map_list.split(',')[0]] = url_map_list.split(',')[1]

    category = '文档书籍'
    query = f"""
        select * from wp_postmeta
        where meta_key = 'cao_downurl_new' and post_id in (
            select object_id from `wp_term_relationships`
            where term_taxonomy_id in (
                select t.term_id from `wp_terms` as t
                inner join `wp_term_taxonomy` tt on t.term_id = tt.term_id
                where t.name = '{category}' and tt.taxonomy = 'category'
            )
        );
    """
    MysqlClientUtils.change_database("res_21zys_com")
    result = MysqlClientUtils.select(query)
    for data in result:
        url = str(phpserialize.loads(bytes(data['meta_value'], encoding='UTF-8'))[0][b'url'], 'UTF-8')
        meta_id = data['meta_id']
        post_id = data['post_id']
        meta_key = data['meta_key']
        meta_value = data['meta_value']
        if url in new_urls.keys() and url not in replaced_links:
            meta_value = meta_value.replace(url, new_urls[url])
            affected_rows = MysqlClientUtils.update("""UPDATE `wp_postmeta` SET meta_value = %s WHERE meta_id = %s AND post_id = %s AND meta_key = %s;""", (meta_value, meta_id, post_id, meta_key))
            if affected_rows is not None and affected_rows != 0:
                RedisUtils.add_set(RedisUtils.res_21zys_com_new_links, new_urls[url])
            print(url)


def test_bulk_insert():
    table_name = 'coser_albums'
    # datas = [
    #     {'album': 'test', 'filename': 'test', 'cloud_filename': 'test', 'image_link': 'test', 'delete_link': 'test'},
    #     {'album': 'test1', 'filename': 'test1', 'cloud_filename': 'test1', 'image_link': 'test1', 'delete_link': 'test1'}
    # ]
    data = {'album': 'album', 'filename': 'filename', 'cloud_filename': 'cloud_filename', 'image_link': 'image_link', 'delete_link': 'delete_link'}
    MysqlClientUtils.insert(table_name, data)


def test_update():
    update_query = "UPDATE coser_albums SET filename = %s WHERE id = %s"
    update_params = ("test3", 1)
    rows_updated = MysqlClientUtils.update(update_query, update_params)
    print(f"Updated {rows_updated} rows")

def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")


if __name__ == "__main__":
    enable_proxy()
    # test_output_category_links()
    test_replace_new_links()
# 用法示例：
# 1. SELECT
# result = MysqlClientUtils.select("SELECT * FROM your_table WHERE id = %s", (1,))
# print(result)

# 2. INSERT
# new_id = MysqlClientUtils.insert("INSERT INTO your_table (name, value) VALUES (%s, %s)", ("test", 123))
# print(new_id)

# 3. UPDATE
# affected_rows = MysqlClientUtils.update("UPDATE your_table SET value = %s WHERE id = %s", (456, 1))
# print(affected_rows)

# 4. DELETE
# deleted_rows = MysqlClientUtils.delete("DELETE FROM your_table WHERE id = %s", (1,))
# print(deleted_rows)