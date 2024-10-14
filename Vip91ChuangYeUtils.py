import os, logging, requests, redis
from datetime import datetime, timedelta
from dateutil import parser
from retrying import retry
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook

class DateUtils:
    @staticmethod
    def get_current_date():
        """获取当前日期"""
        return datetime.now().date()

    @staticmethod
    def get_current_datetime():
        """获取当前日期时间"""
        return datetime.now()

    @staticmethod
    def get_current_datetime_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """返回当前日期时间字符串，格式: 2024-09-08 01:32:08"""
        return datetime.now().strftime(fmt)

    @staticmethod
    def str_to_date(date_str: str, fmt: str = "%Y-%m-%d") -> datetime.date:
        """将字符串转换为日期"""
        return datetime.strptime(date_str, fmt).date()

    @staticmethod
    def date_to_str(date: datetime.date, fmt: str = "%Y-%m-%d") -> str:
        """将日期转换为字符串"""
        return date.strftime(fmt)
        
    @staticmethod
    def iso_str_to_datetime(iso_str: str) -> datetime:
        """将带时区的 ISO 8601 格式时间字符串转换为 datetime 对象"""
        return parser.parse(iso_str)

    @staticmethod
    def add_days(date: datetime.date, days: int) -> datetime.date:
        """在指定日期基础上增加或减少天数"""
        return date + timedelta(days=days)

    @staticmethod
    def add_months(date: datetime.date, months: int) -> datetime.date:
        """在指定日期基础上增加或减少月份"""
        return date + relativedelta(months=months)

    @staticmethod
    def days_between(date1: datetime.date, date2: datetime.date) -> int:
        """计算两个日期之间的天数差"""
        return (date2 - date1).days

    @staticmethod
    def date_to_datetime(date_obj: datetime.date) -> datetime:
        """将 date 对象转换为 datetime 对象"""
        return datetime.combine(date_obj, datetime.min.time())

    @staticmethod
    def datetime_to_date(datetime_obj: datetime) -> datetime.date:
        """将 datetime 对象转换为 date 对象"""
        return datetime_obj.date()

    @staticmethod
    def is_valid_date(date_str: str, fmt: str = "%Y-%m-%d") -> bool:
        """判断字符串是否为合法的日期格式"""
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_current_year():
        """获取当前年份"""
        return datetime.now().year

    @staticmethod
    def get_current_month():
        """获取当前月份"""
        return datetime.now().month

    @staticmethod
    def get_current_day():
        """获取当前日期中的日"""
        return datetime.now().day

    @staticmethod
    def get_timezone_aware_datetime(timezone_str: str = 'UTC'):
        """返回指定时区的当前时间"""
        tz = pytz.timezone(timezone_str)
        return datetime.now(tz)

class RedisUtils:
    # Redis 连接属性，用户提供
    host = "152.32.175.149"
    port = 6379
    db = 0
    password = 'Mh359687..'
    vip_91_article_links = 'vip_91_article_links'
    # 私有构造函数
    _redis_client = None

    @classmethod
    def _initialize_client(cls):
        if cls._redis_client is None:
            cls._redis_client = redis.StrictRedis(
                host=cls.host,
                port=cls.port,
                db=cls.db,
                password=cls.password,
                decode_responses=True
            )

    # ------------------ String 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def set_string(cls, key: str, value: str):
        cls._initialize_client()
        return cls._redis_client.set(key, value)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_string(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.get(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def del_key(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.delete(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def update_string(cls, key: str, value: str):
        cls._initialize_client()
        return cls._redis_client.set(key, value)

    # ------------------ List 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def push_list(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.rpush(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_list(cls, key: str, start: int = 0, end: int = -1):
        cls._initialize_client()
        return cls._redis_client.lrange(key, start, end)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def pop_list(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.lpop(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def list_length(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.llen(key)

    # ------------------ Set 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def add_set(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.sadd(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_set(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.smembers(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def rem_set(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.srem(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def set_length(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.scard(key)

    # ------------------ Hash 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def set_hash(cls, key: str, field: str, value: str):
        cls._initialize_client()
        return cls._redis_client.hset(key, field, value)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_hash(cls, key: str, field: str):
        cls._initialize_client()
        return cls._redis_client.hget(key, field)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_all_hash(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.hgetall(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def del_hash(cls, key: str, field: str):
        cls._initialize_client()
        return cls._redis_client.hdel(key, field)

    # ------------------ Zset 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def add_zset(cls, key: str, score: float, value: str):
        cls._initialize_client()
        return cls._redis_client.zadd(key, {value: score})

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_zset(cls, key: str, start: int = 0, end: int = -1, withscores: bool = False):
        cls._initialize_client()
        return cls._redis_client.zrange(key, start, end, withscores=withscores)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def rem_zset(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.zrem(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def zset_length(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.zcard(key)

# 配置日志
class Vip91ChuangYeUtils:
    cookie: str = r"PHPSESSID=6eus0ie5ct64agdoh4nn9g77al; wordpress_logged_in_af89e27944e71791976296dfc34e93be=21zys%7C1730004426%7C4FtkE05uoiJ9pDUxEGreweZlj0WMZU5ocjnVG60Sgct%7C452da74eac58527be8392363a37416b8cc2fa9b67aa9b12a6e1e18868d8baf0b"
    log_file_path = os.path.join(os.getcwd(), "file", "log.txt")

    # 初始化日志系统
    logging.basicConfig(filename=log_file_path,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def convert_cookie_to_dict(cookie_str):
        """
        将字符串类型的cookie转换为requests模块需要的字典格式
        :param cookie_str: 字符串类型的cookie (格式为 "key1=value1; key2=value2; ...")
        :return: 字典类型的cookie
        """
        cookies = {}
        # 通过分号分割各个键值对
        cookie_items = cookie_str.split(';')

        # 遍历每个键值对，去掉空白并将它们添加到字典中
        for item in cookie_items:
            key, value = item.strip().split('=', 1)
            cookies[key] = value

        return cookies

    @staticmethod
    def fetch_url(url: str, retries=1):
        """发送HTTP请求，默认重试1次"""
        logging.info(f"Fetching URL: {url}")
        attempt = 0
        while attempt <= retries:
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logging.error(f"Error fetching URL: {url}, attempt {attempt + 1}, Error: {e}")
                if attempt == retries:
                    return None  # 超过最大重试次数，返回None
                attempt += 1
            

    @staticmethod
    def get_vip_practical_project_links(base_url: str = "https://vip.91chuangye.cn/scxm",
                                  is_ouput_xlsx: bool = False,
                                  xlsx_file_path: str = os.path.join(os.getcwd(), "file", "vip_91chuangye_com.xlsx")):
        page = 1
        published_article_links = RedisUtils.get_set(RedisUtils.vip_91_article_links)
        flag = True
        while flag:
            if page != 1:
                url = f"{base_url}/page/{page}"
            else:
                url = base_url
            html_content = Vip91ChuangYeUtils.fetch_url(url)

            if not html_content:
                break  # 如果请求失败，退出循环

            soup = BeautifulSoup(html_content, 'html.parser')
            
            post_wrapper = soup.find('div', class_='row posts-wrapper scroll')
            
            item_list = post_wrapper.find_all('div', recursive=False) if post_wrapper else []
            results = []
            for item in item_list:
                try:
                
                    # 提取title和link
                    entry_wrapper = item.find('div', class_='entry-wrapper')
                    title_tag = entry_wrapper.find('h2', class_='entry-title').find('a')
                    title = title_tag.text.strip()
                    link = title_tag['href']

                    if published_article_links and link in published_article_links:
                        Vip91ChuangYeUtils.append_to_xlsx(xlsx_file_path, results)
                        results = []
                        flag = False
                        break
                    
                    # 提取cover
                    cover_tag = item.find('div', class_='entry-media').find('img')
                    cover = cover_tag['data-src'] if cover_tag else None

                    # 提取category
                    category_tags = entry_wrapper.find('span', class_='meta-category-dot').find_all('a')
                    category = ",".join(a.text.strip() for a in category_tags)
                    
                    publish_date_tags = entry_wrapper.find('span', class_='meta-date').find('time')
                    publish_date = DateUtils.iso_str_to_datetime(publish_date_tags['datetime']) if publish_date_tags else DateUtils.get_current_datetime()
                    
                    logging.info(f"Link: {link}, Title: {title}, Cover: {cover}, Category: {category}, Publish_date: {publish_date}")
                    results.append([link, title, cover, category, publish_date])
                except Exception as e:
                    logging.error(f"Error processing article: {e}")
                    continue

            # 将结果追加到xlsx文件中
            Vip91ChuangYeUtils.append_to_xlsx(xlsx_file_path, results)

            # 下一页
            page += 1


    @staticmethod
    def append_to_xlsx(file_path, data):
        """将提取到的结果追加到现有的xlsx文件中，如果不存在则创建新文件"""
        if not os.path.exists(file_path):
            # 如果文件不存在，创建新文件并添加表头
            wb = Workbook()
            ws = wb.active
            ws.title = "Results"
            ws.append(["Link", "Title", "Cover", "Category", "Publis_date"])  # 添加表头
            wb.save(file_path)
            logging.info(f"Created new file and saved to {file_path}")

        # 追加数据
        wb = load_workbook(file_path)
        ws = wb.active
        for row in data:
            ws.append(row)  # 追加每一行数据
        wb.save(file_path)
        logging.info(f"Appended data to {file_path}")


def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")

if __name__ == "__main__":
    enable_proxy()
    # 调用静态方法执行操作
    Vip91ChuangYeUtils.get_vip_practical_project_links()
