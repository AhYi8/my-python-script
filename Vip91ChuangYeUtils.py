import os, logging, requests, redis
from retrying import retry
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook

class RedisUtils:
    # Redis 连接属性，用户提供
    host = "152.32.175.149"
    port = 6379
    db = 0
    password = 'Mh359687..'
    vip_91_chuangye = "vip_91_chuangye_article_links"
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
    def get_vip_practical_project(base_url: str = "https://vip.91chuangye.cn/scxm",
                                  xlsx_file_path: str = os.path.join(os.getcwd(), "file", "results.xlsx")):
        page = 1
        published_article_links = RedisUtils.get_set(RedisUtils.vip_91_chuangye)
        flag = True
        while flag:
            if page != 1:
                url = f"base_url/page/{page}"
            else:
                url = base_url
            html_content = Vip91ChuangYeUtils.fetch_url(url)

            if not html_content:
                break  # 如果请求失败，退出循环

            soup = BeautifulSoup(html_content, 'html.parser')
            main_div = soup.find(id="main")

            # 查找目标内容
            article_div_list = main_div.select("div.archive.container div.row div.content-area div.row.posts-wrapper.scroll div")
            if not article_div_list:
                logging.info(f"No articles found on page {page}. Terminating.")
                break

            results = []

            # 遍历并提取所需信息
            for article_div in article_div_list:
                try:
                    # 获取链接和标题
                    a_tag = article_div.select_one("article div.entry-wrapper header.entry-header a")
                    link = a_tag['href']
                    title = a_tag.get_text(strip=True)

                    if published_article_links and link in published_article_links:
                        Vip91ChuangYeUtils.append_to_xlsx(xlsx_file_path, results)
                        flag = False
                        break

                    Vip91ChuangYeUtils.get_article(link)

                    # 获取类别
                    category_a_list = article_div.select("article div.entry-wrapper span.meta-category-dot a")
                    category = ",".join([a.get_text(strip=True) for a in category_a_list])

                    # 获取封面图片链接
                    img_tag = article_div.select_one("article div.entry-media div img")
                    cover = img_tag['data-src'] if img_tag else None

                    logging.info(f"Title: {title}, Link: {link}, Category: {category}, Cover: {cover}")
                    results.append([title, link, category, cover])

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
            ws.append(["Title", "Link", "Category", "Cover"])  # 添加表头
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
    Vip91ChuangYeUtils.get_vip_practical_project()
