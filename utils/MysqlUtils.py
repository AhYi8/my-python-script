import mysql.connector, time, os, phpserialize
from typing import List, Dict
from mysql.connector import Error
from datetime import datetime
from .FileUtils import FileUtils
from .RedisUtils import RedisUtils

class MysqlUtils:
    # 饿汉式单例 - 初始化时即创建数据库连接
    _connection = None
    _table_columns_cache = {}
    _checked_log_tables = set()  # 缓存已经检查过的日志表
    _enable_logging = False  # 默认不开启日志

    # 静态方法，直接初始化数据库连接（用户可在此修改自己的配置）
    @staticmethod
    def _initialize_connection(host='152.32.175.149', port=3306, user='21zys', password='Mh359687..', database='my_database'):
        try:
            if MysqlUtils._connection is None:
                MysqlUtils._connection = mysql.connector.connect(
                    host=host,  # 替换为你的host
                    port=port,  # 替换为你的端口
                    user=user,  # 替换为你的用户名
                    password=password,  # 替换为你的密码
                    database=database  # 替换为你的数据库名
                )
                if MysqlUtils._connection.is_connected():
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
        if table_name in MysqlUtils._table_columns_cache:
            return MysqlUtils._table_columns_cache[table_name]

        MysqlUtils._initialize_connection()
        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor()
            query = f"""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = DATABASE()
                """
            cursor.execute(query, (table_name,))
            columns = [row[0] for row in cursor.fetchall()]
            MysqlUtils._table_columns_cache[table_name] = columns  # 缓存列名
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

        if log_table_name in MysqlUtils._checked_log_tables:
            return  # 如果已经检查过该日志表，直接返回

        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor()

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
                MysqlUtils._connection.commit()
                print(f"Log table '{log_table_name}' created.")

            # 记录已检查过的日志表
            MysqlUtils._checked_log_tables.add(log_table_name)
        except Error as e:
            print(f"Error creating log table {log_table_name}: {e}")
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _log_operation(table_name: str, full_query: str, affected_rows: int):
        """将完整SQL操作记录到 {table_name}_log 表"""
        MysqlUtils._create_log_table_if_not_exists(table_name)  # 自动创建日志表（如果不存在）

        log_table_name = f"{table_name}_log"
        log_query = f"""
            INSERT INTO {log_table_name} (full_query, affected_rows, create_time) 
            VALUES (%s, %s, %s)
            """
        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor()
            current_time = MysqlUtils._get_current_time()  # 获取当前时间作为日志时间
            cursor.execute(log_query, (full_query, affected_rows, current_time))
            MysqlUtils._connection.commit()
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
        MysqlUtils._enable_logging = True

    @staticmethod
    def change_database(database_name: str):
        """切换当前数据库"""
        cursor = None
        try:
            MysqlUtils._initialize_connection()
            cursor = MysqlUtils._connection.cursor()
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
        if MysqlUtils._connection is not None:
            MysqlUtils._connection.close()
            MysqlUtils._connection = None
        MysqlUtils._initialize_connection(host, port, user, password, database)


    # 执行INSERT操作
    @staticmethod
    def insert(table_name: str, params: Dict[str, any], auto_fill_timestamps: bool = False, max_retries=3, retry_delay=2):
        """插入单条数据，带重试机制"""
        MysqlUtils._initialize_connection()

        # 自动填充 create_time 和 update_time
        if auto_fill_timestamps:
            current_time = MysqlUtils._get_current_time()
            if 'create_time' not in params:
                params['create_time'] = current_time
            if 'update_time' not in params:
                params['update_time'] = current_time

        # 检查字段是否与表结构匹配
        valid_columns = MysqlUtils._get_table_columns(table_name)
        invalid_columns = [key for key in params.keys() if key not in valid_columns]
        if invalid_columns:
            raise ValueError(f"Invalid columns for table {table_name}: {invalid_columns}")

        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor()
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
                MysqlUtils._connection.commit()
                return cursor.rowcount, cursor.lastrowid

            affected_rows, last_insert_id = MysqlUtils._execute_with_retries(execute_insert, max_retries,
                                                                             retry_delay)

            # 记录完整的 SQL 语句到日志
            if MysqlUtils._enable_logging:
                full_query = MysqlUtils._format_query(query, values)
                MysqlUtils._log_operation(table_name, full_query, affected_rows)

            return last_insert_id  # 返回插入行的ID
        except Error as e:
            print(f"Error executing INSERT query: {e}")
            MysqlUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def bulk_insert(table: str, data: List[Dict[str, any]], auto_fill_timestamps: bool = False, max_retries=3,
                    retry_delay=2):
        """批量插入数据，带重试机制"""
        MysqlUtils._initialize_connection()

        if not data:
            raise ValueError("Data list is empty")
        if not isinstance(data, List):
            raise ValueError("Data is not a List")
        # 如果自动填充时间戳，检查并填充create_time和update_time字段
        if auto_fill_timestamps:
            current_time = MysqlUtils._get_current_time()
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
            cursor = MysqlUtils._connection.cursor()

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
                MysqlUtils._connection.commit()
                return cursor.rowcount

            affected_rows = MysqlUtils._execute_with_retries(execute_bulk_insert, max_retries, retry_delay)

            # 记录完整的 SQL 语句到日志
            if MysqlUtils._enable_logging:
                values = [f"""({','.join([f"'{row[field]}'" for field in first_row_fields])})""" for row in data]
                full_query = f"""INSERT INTO {table} ({fields}) VALUES {','.join(values)};"""
                MysqlUtils._log_operation(table, full_query, affected_rows)

            return affected_rows  # 返回插入的行数
        except Error as e:
            print(f"Error executing BULK INSERT query: {e}")
            MysqlUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def update(query: str, params: tuple, auto_update_timestamp: bool = False, max_retries=3, retry_delay=2):
        """更新数据，带重试机制"""
        MysqlUtils._initialize_connection()

        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor()
            if auto_update_timestamp:
                # 如果需要自动更新 update_time 字段，添加到 SQL 和参数中
                current_time = MysqlUtils._get_current_time()
                query = query.replace("SET", "SET update_time = %s,", 1)  # 在 SET 后插入 update_time 字段
                params = (current_time,) + params  # 将当前时间插入参数前面

            # 执行更新操作，使用重试机制
            def execute_update():
                cursor.execute(query, params)
                MysqlUtils._connection.commit()
                return cursor.rowcount

            affected_rows = MysqlUtils._execute_with_retries(execute_update, max_retries, retry_delay)

            # 记录完整的 SQL 语句到日志
            if MysqlUtils._enable_logging:
                full_query = MysqlUtils._format_query(query, params)
                MysqlUtils._log_operation(query.split()[1], full_query, affected_rows)

            return affected_rows
        except Error as e:
            print(f"Error executing UPDATE query: {e}")
            MysqlUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    # 执行DELETE操作
    @staticmethod
    def delete(query, params):
        MysqlUtils._initialize_connection()
        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor()
            cursor.execute(query, params)
            MysqlUtils._connection.commit()
            return cursor.rowcount  # 返回受影响的行数
        except Error as e:
            print(f"Error executing DELETE query: {e}")
            MysqlUtils._connection.rollback()
        finally:
            if cursor:
                cursor.close()

    # 执行SELECT查询
    @staticmethod
    def select(query, params=None):
        MysqlUtils._initialize_connection()
        cursor = None
        try:
            cursor = MysqlUtils._connection.cursor(dictionary=True)
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
    MysqlUtils.change_database("res_21zys_com")
    result = MysqlUtils.select(query)
    urls = []
    for data in result:
        url = str(phpserialize.loads(bytes(data['meta_value'], encoding='UTF-8'))[0][b'url'], 'UTF-8')
        if 'pan.quark.cn' in url and url not in replaced_links:
            urls.append(url)
    FileUtils.write_lines(r"C:\Users\Administrator\Desktop\old_urls.csv", urls)


def test_replace_new_links():
    replaced_links = RedisUtils.get_set(RedisUtils.res_21zys_com_new_links)
    new_urls = {}
    for url_map_list in FileUtils.read_lines(r"C:\Users\Administrator\Desktop\new_urls.txt", is_strip=True):
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
    MysqlUtils.change_database("res_21zys_com")
    result = MysqlUtils.select(query)
    for data in result:
        url = str(phpserialize.loads(bytes(data['meta_value'], encoding='UTF-8'))[0][b'url'], 'UTF-8')
        meta_id = data['meta_id']
        post_id = data['post_id']
        meta_key = data['meta_key']
        meta_value = data['meta_value']
        if url in new_urls.keys() and url not in replaced_links:
            meta_value = meta_value.replace(url, new_urls[url])
            affected_rows = MysqlUtils.update("""UPDATE `wp_postmeta` SET meta_value = %s WHERE meta_id = %s AND post_id = %s AND meta_key = %s;""", (meta_value, meta_id, post_id, meta_key))
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
    MysqlUtils.insert(table_name, data)


def test_update():
    update_query = "UPDATE coser_albums SET filename = %s WHERE id = %s"
    update_params = ("test3", 1)
    rows_updated = MysqlUtils.update(update_query, update_params)
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