from wordpress_xmlrpc import Client, WordPressPost, ServerConnectionError
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, EditPost, DeletePost, GetPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.methods import taxonomies
from wordpress_xmlrpc import WordPressTerm
from wordpress_xmlrpc.compat import xmlrpc_client
from openpyxl import Workbook
import pandas as pd
from typing import List
import phpserialize, collections.abc, requests, hashlib, uuid, random, string, time, os, re, openpyxl, shutil, redis
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime

collections.Iterable = collections.abc.Iterable

class RedisUtils:
    # Redis 连接属性，用户提供
    host = "152.32.175.149"
    port = 6379
    db = 0
    password = 'Mh359687..'

    res_21zys_com_titles_key = 'res.21zys.com_titles'

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


class Article:
    title: str
    content: str
    post_status: str
    terms_names: {}
    custom_fields: []

    def __init__(self):
        super()


class ArticleMeta:
    title: str = ''
    image: str = ''
    content: str = ''
    status: str = ''
    tags: str = ''
    category: str = ''
    cao_price: str = '0'
    cao_vip_rate: str = '0.6'
    cao_is_boosvip: str = '1'
    cao_close_novip_pay: str = '0'
    cao_paynum: str = '0'
    cao_status: str = '1'
    source_name: str = ''
    source_url: str = ''
    pwd: str = ''
    cao_info: str = ''
    cao_demourl: str = ''
    cao_diy_btn: str = ''
    cao_video: str = ''
    cao_is_video_free: str = ''
    video_url_new: str = ''
    post_titie: str = ''
    keywords: str = ''
    description: str = ''

    def __init__(self, title=None, image=None, content=None, status=None, tags=None, category=None, cao_price=None, source_url=None, pwd=None):
        self.title = title
        self.image = image
        self.content = content
        self.status = status
        self.tags = tags
        self.category = category
        self.cao_price = cao_price
        self.source_name = title
        self.source_url = source_url
        self.pwd = pwd

    def __repr__(self):
        return f"ArticleMeta(title={self.title}, image={self.image}, content={self.content}, status={self.status}, tags={self.tags}, category={self.category}, cao_price={self.cao_price}, source_name={self.source_name}, source_url={self.source_url}, pwd={self.pwd})"

    def get_status(self):
        if self.status == '私密':
            return 'private'
        if self.status == '公开' or self.status == '':
            return 'publish'
        if self.status == '草稿':
            return 'draft'
        if self.status == '未发布':
            return 'undo'

    def get_tags(self):
        if self.tags != '':
            return self.tags.replace('，', ',').split(',')
        return []

    def get_category(self):
        if self.category != '':
            return self.category.replace('，', ',').split(',')
        return []

    def get_cao_is_bossvip(self):
        if self.cao_is_boosvip == '是':
            return '1'
        elif self.cao_is_boosvip == '否':
            return '0'
        return '1'

    def get_cao_close_novip_pay(self):
        if self.cao_close_novip_pay == '是':
            return '1'
        elif self.cao_close_novip_pay == '否':
            return '0'
        return '0'

    def get_cao_status(self):
        if self.cao_status == '是':
            return '1'
        elif self.cao_status == '否':
            return '0'
        return '1'

    def get_cao_pwd(self):
        if self.pwd:
            return self.pwd
        return ''
class WordpressUtils:
    wp = Client(
        r'http://res.21zys.com/xmlrpc_Mh359687...php',
        '21zys',
        'Mh359687..'
    )


    @staticmethod
    def get_all_tag_name():
        return {tag.name for tag in WordpressUtils.wp.call(taxonomies.GetTerms('post_tag'))}

    @staticmethod
    def get_all_post(number=100, offset=0, limit=0):
        all_posts = []
        while True:
            try:
                # 获取一部分文章，使用 offset 和 number 控制
                posts = WordpressUtils.wp.call(GetPosts({'number': number, 'offset': offset}))
                if not posts:
                    break  # 如果没有返回文章，说明已经获取完毕
                all_posts.extend(posts)
                if limit != 0 and len(all_posts) >= limit:
                    break
                offset += number  # 更新 offset，以便获取下一部分文章
            except ServerConnectionError as e:
                print(f"Connection error: {e}")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break
        return all_posts

    @staticmethod
    def post_article(article: Article):
        try:
            post = WordPressPost()
            post.title = article.title
            post.content = article.content
            post.post_status = article.post_status
            post.terms_names = article.terms_names
            post.custom_fields = article.custom_fields
            post.comment_status = 'open'
            post.id = WordpressUtils.wp.call(NewPost(post))
            if article.post_status == 'publish':
                RedisUtils.add_set(RedisUtils.res_21zys_com_titles_key, article.title)
            return post.id
        except Exception as e:
            print(f"发布文章失败：{e}")


    @staticmethod
    def post_articles(articles: List[Article]):
        total = len(articles)
        zfill_size = len(str(total))
        index = 1
        for article in articles:
            print(f"{str(index).zfill(zfill_size)}/{total}-->正在发布：{article.title}")
            index += 1
            WordpressUtils.post_article(article)

    @staticmethod
    def read_xlsx_to_article_metas(file_path, field_mapping):
        """
        读取指定路径的xlsx文件，将中文表头映射到对象字段上，并返回对象列表。

        :param file_path: xlsx文件的路径
        :param field_mapping: 中文表头到对象字段的映射字典
        :return: 包含对象的列表
        """
        # 使用 pandas 读取 xlsx 文件
        df = pd.read_excel(file_path, engine='openpyxl')

        # 将所有NaN值替换为空字符串
        df.fillna('', inplace=True)

        # 将 DataFrame 的列名替换为对象的字段名
        df.rename(columns=field_mapping, inplace=True)

        # 遍历 DataFrame 行并转换为对象
        article_metas = []
        for _, row in df.iterrows():
            obj = ArticleMeta(**row.to_dict())
            article_metas.append(obj)

        return article_metas

    @staticmethod
    def article_metas_to_articles(base_image_path: str, article_metas: List[ArticleMeta]):
        articles: List[Article] = []
        tag_names = WordpressUtils.get_all_tag_name()
        post_titles = RedisUtils.get_set(RedisUtils.res_21zys_com_titles_key)
        if not post_titles:
            post_titles = {post.title for post in WordpressUtils.get_all_post()}
            RedisUtils.add_set(RedisUtils.res_21zys_com_titles_key, *post_titles)
        total = len(article_metas)
        zfill_size = len(str(total))
        index = 1
        for article_meta in article_metas:
            if article_meta.title in post_titles or article_meta.get_status() == 'undo':
                print(f'{str(index).zfill(zfill_size)}/{total}-->已存在同名文章或未发布文章，跳过发布，请手动处理：{article_meta.title}')
                index += 1
                continue
            article = Article()
            imgurl = ''
            while not imgurl and article_meta.get_status() == 'publish':
                try:
                    if article_meta.image and article_meta.image != '无':
                        if 'loli.net' in article_meta.image or 's3.bmp.ovh' in article_meta.image or 's3.uuu.ovh' in article_meta.image:
                            imgurl = article_meta.image
                        else:
                            filename, imgurl, _ = ImageUtils.upload_to_smms_by_image_url(article_meta.image, article_meta.title)
                    else:
                        image_path = ImageUtils.find_first_image_with_text(base_image_path, article_meta.title)
                        if image_path:
                            _, imgurl, deleteUrl = ImageUtils.upload_to_smms_image(image_path)
                            # _, imgurl = ImageUtils.upload_to_imgurl_image(image_path)
                        else:
                            print(f'{str(index).zfill(zfill_size)}/{total}-->图片上传失败，请手动处理：{article_meta.title}')
                            index += 1
                            continue
                except Exception as e:
                    # print(f'{str(index).zfill(zfill_size)}/{total}-->上传图片失败，正在重试...')
                    print(f'上传图片失败：{e}')
            print(f'{str(index).zfill(zfill_size)}/{total}-->{article_meta.title}, {imgurl}')
            article.title = article_meta.title
            post_titles.add(article.title)
            article.content = f"<img class='aligncenter' src='{imgurl}'>\n\n{article_meta.content}"
            article.post_status = article_meta.get_status()
            # 自动添加标签
            tag_names.update(article_meta.get_tags())
            tags = {tag_name for tag_name in tag_names if tag_name in article_meta.content or tag_name in article_meta.title}
            tags.update(article_meta.get_tags())
            terms_names = {'post_tag': list(tags), 'category': article_meta.get_category()}
            article.terms_names = terms_names
            cao_downurl_new = [
                {'name': article_meta.source_name, 'url': article_meta.source_url, 'pwd': article_meta.get_cao_pwd()}
            ]
            keywords = []
            keywords.extend(article_meta.get_tags())
            keywords.extend(article_meta.get_category())
            custom_fields = [
                {'key': 'cao_price', 'value': article_meta.cao_price},
                {'key': 'cao_vip_rate', 'value': article_meta.cao_vip_rate},
                {'key': 'cao_is_boosvip', 'value': article_meta.get_cao_is_bossvip()},
                {'key': 'cao_close_novip_pay', 'value': article_meta.get_cao_close_novip_pay()},
                {'key': 'cao_paynum', 'value': article_meta.cao_paynum},
                {'key': 'cao_status', 'value': article_meta.get_cao_status()},
                {'key': 'cao_downurl_new', 'value': cao_downurl_new},
                {'key': 'cao_info', 'value': article_meta.cao_info},
                {'key': 'cao_demourl', 'value': article_meta.cao_demourl},
                {'key': 'cao_diy_btn', 'value': article_meta.cao_diy_btn},
                {'key': 'cao_video', 'value': article_meta.cao_video},
                {'key': 'cao_is_video_free', 'value': article_meta.cao_is_video_free},
                {'key': 'video_url_new', 'value': article_meta.video_url_new},
                {'key': 'post_titie', 'value': article_meta.title},
                {'key': 'keywords', 'value': ','.join(keywords)},
                {'key': 'description', 'value': article_meta.content},
                {'key': 'views', 'value': str(random.randint(300, 500))}
            ]
            article.custom_fields = custom_fields
            articles.append(article)
            index += 1
        return articles

    @staticmethod
    def outport_article(number=100, offset=0, limit=0):
        posts = WordpressUtils.get_all_post(number, offset, limit)
        taxonomies = set()
        for post in posts:
            id = post.id  # 文章 id
            user = post.user  # 文章用户 id
            date = str(post.date)  # 创建日期
            date_modified = str(post.date_modified)  # 最后一次修改日期
            slug = post.slug  # 类似 title, url 编码
            post_status = post.post_status  # publish, private, draft
            title = post.title  # 标题
            content = post.content  # 内容
            excerpt = post.excerpt  # 空值
            link = post.link  # 文章链接
            comment_status = post.comment_status  # open, close
            ping_status = post.ping_status  # open, close
            terms = post.terms  # 分类目录和标签
            custom_fileds = post.custom_fields  # 自定义字段
            password = post.password  # 密码保护
            post_format = post.post_format  # 形式：标准: standard，图片: image，视频: video，音频: audio
            thumbnail = post.thumbnail  # 缩率图
            sticky = post.sticky
            post_type = post.post_type

            categories = []
            tags = []
            series = []
            for term in terms:
                if term.taxonomy == 'category':
                    categories.append(term.name)
                elif term.taxonomy == 'post_tag':
                    tags.append(term.name)
                elif term.taxonomy == 'series':
                    series.append(term.name)

            temp_post = []
            cao_downurl_new: str
            for field in custom_fileds:
                key = field['key']
                value = field['value']
                if key == 'cao_downurl_new':
                    cao_downurl_new = value
            for field in custom_fileds:
                key = field['key']
                value = field['value']
                if key == 'cao_price':
                    if cao_downurl_new:
                        name_url_password_bytes = phpserialize.loads(bytes(cao_downurl_new, encoding='utf-8'))
                        name_url_password = \
                        [value for value in DataUtils.decode_bytes(name_url_password_bytes).values()][0]
                        name = name_url_password['name']
                        url = name_url_password['url']
                        password = name_url_password['pwd']
                        DataUtils.output_data_to_xlsx(('title', 'categories', 'url'),
                                                      (title, ','.join(categories), url),
                                                      r'C:\Users\MAC\Desktop\wordpress_articles_output.xlsx')

class ImageUtils:
    smms_token: str = 'tbVH1tVAwadESF2NdCXrr27UuqmGtNCq'
    imgURL_uid: str = 'b77b5646d741207bc920f2fd3daa3490'
    imgURL_token: str = '6e6c36de4eaaf95bd74b280259f18dd7'
    imgURL_album_id: int = 413
    water: str = 'res.21zys.com'
    pattern: str = 'res.21zys.com-{Y}{m}{d}{h}{i}{s}'
    auto_increment: int = 1

    @staticmethod
    def find_first_image_with_text(directory, search_string):
        for root, _, files in os.walk(directory):
            for file in files:
                if search_string in file and file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    return os.path.join(root, file)
        return None

    @staticmethod
    def add_watermark(image_path, watermark_text):
        """
        读取读取指定路径的图片，添加水印文本

        :param image_path: img图片路径
        :param watermark_text: 水印文本
        :return: img 流
        """
        image = Image.open(image_path)
        watermark_image = image.copy()
        draw = ImageDraw.Draw(watermark_image)

        font_size = int(min(image.size) * 0.15)  # 水印字体大小
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)

        # 创建透明图层用于绘制水印
        watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))
        draw_watermark = ImageDraw.Draw(watermark_layer)

        # 计算文本的宽度和高度
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # 计算水印的位置（居中）
        x = (watermark_layer.width - text_width) / 2
        y = (watermark_layer.height - text_height) / 2

        # 设置透明度（255为不透明）
        fill = (0, 0, 0, int(255 * 0.6))  # 黑色，透明度为0.4

        # 添加水印文本
        draw_watermark.text((x, y), watermark_text, font=font, fill=fill)

        # 旋转水印图层45度
        watermark_layer = watermark_layer.rotate(45, expand=True)

        # 创建一个与原始图像尺寸相同的空白图像
        full_watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))

        # 计算旋转后图层的位置以居中对齐
        paste_x = (full_watermark_layer.width - watermark_layer.width) // 2
        paste_y = (full_watermark_layer.height - watermark_layer.height) // 2

        # 将旋转后的水印图层粘贴到空白图像上
        full_watermark_layer.paste(watermark_layer, (paste_x, paste_y), watermark_layer)

        # 将水印图层与原始图像合并
        watermarked_image = Image.alpha_composite(watermark_image.convert('RGBA'), full_watermark_layer)

        watermarked_io = BytesIO()
        watermarked_image.convert('RGB').save(watermarked_io, format=image.format)
        watermarked_io.seek(0)
        return watermarked_io

    @staticmethod
    def add_watermark_to_image(image, watermark_text):
        watermark_image = image.copy()
        draw = ImageDraw.Draw(watermark_image)

        font_size = int(min(image.size) * 0.15)  # 水印字体大小
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)

        # 创建透明图层用于绘制水印
        watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))
        draw_watermark = ImageDraw.Draw(watermark_layer)

        # 计算文本的宽度和高度
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # 计算水印的位置（居中）
        x = (watermark_layer.width - text_width) / 2
        y = (watermark_layer.height - text_height) / 2

        # 设置透明度（255为不透明）
        fill = (0, 0, 0, int(255 * 0.6))  # 黑色，透明度为0.4

        # 添加水印文本
        draw_watermark.text((x, y), watermark_text, font=font, fill=fill)

        # 旋转水印图层45度
        watermark_layer = watermark_layer.rotate(45, expand=True)

        # 创建一个与原始图像尺寸相同的空白图像
        full_watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))

        # 计算旋转后图层的位置以居中对齐
        paste_x = (full_watermark_layer.width - watermark_layer.width) // 2
        paste_y = (full_watermark_layer.height - watermark_layer.height) // 2

        # 将旋转后的水印图层粘贴到空白图像上
        full_watermark_layer.paste(watermark_layer, (paste_x, paste_y), watermark_layer)

        # 将水印图层与原始图像合并
        watermarked_image = Image.alpha_composite(watermark_image.convert('RGBA'), full_watermark_layer)

        watermarked_io = BytesIO()
        watermarked_image.convert('RGB').save(watermarked_io, format=image.format)
        watermarked_io.seek(0)
        return watermarked_io

    @staticmethod
    def generate_filename(filename, pattern, auto_increment):
        """
        返回格式化的文件名，用于smms上传时的文件名格式化

        :param filename: 原文件名
        :param pattern: 格式化模板
        :param auto_increment: 自增序列
        :return: 格式化后的文件名
        """
        base, ext = filename.rsplit('.', 1)
        now = datetime.now()

        replacements = {
            '{Y}': now.strftime('%Y'),
            '{y}': now.strftime('%y'),
            '{m}': now.strftime('%m'),
            '{d}': now.strftime('%d'),
            '{h}': now.strftime('%H'),
            '{i}': now.strftime('%M'),
            '{s}': now.strftime('%S'),
            '{ms}': now.strftime('%f')[:3],
            '{timestamp}': str(int(now.timestamp())),
            '{md5}': hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
            '{md5-16}': hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16],
            '{uuid}': str(uuid.uuid4()),
            '{str-6}': ''.join(random.choices(string.ascii_letters + string.digits, k=6)),
            '{filename}': base,
            '{auto}': str(auto_increment)
        }

        for key, value in replacements.items():
            pattern = pattern.replace(key, value)

        return pattern + '.' + ext

    @staticmethod
    def upload_to_smms_image(image_path):
        """
        上传本地文件到smms图床，期间需要格式化文件名，添加水印

        :param image_path: 本地图片路径
        :return: (原文件名, imgURL)
        """
        # 添加水印
        watermarked_image = ImageUtils.add_watermark(image_path, ImageUtils.water)

        # 获取原文件名去掉后缀部分
        original_filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        new_filename = ImageUtils.generate_filename(image_path.rsplit('/', 1)[-1], ImageUtils.pattern,
                                                    ImageUtils.auto_increment)

        url = "https://sm.ms/api/v2/upload"
        headers = {'Authorization': ImageUtils.smms_token}
        files = {'smfile': (new_filename, watermarked_image)}

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if response.status_code == 200 and result['success']:
            return original_filename, result['data']['url'], result['data']['delete']
        else:
            raise Exception(f"Upload to SMMS failed: {result.get('message', 'Unknown error')}")

    def upload_to_smms_by_image_url(image_url, original_filename):
        """
        上传网络文件到smms图床，期间需要格式化文件名，添加水印

        :param image_url: 本地图片路径
        :return: (原文件名, imgURL)
        """

        # 下载图片
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception("Failed to download image.")

        image = Image.open(BytesIO(response.content))
        try:
            # 获取原始文件名后缀
            file_suffix = image_url.rsplit('/', 1)[-1].rsplit('.', 1)[1]
        except Exception as e:
            file_suffix = 'jpg'

        # 添加水印
        watermarked_image_io = ImageUtils.add_watermark_to_image(image, ImageUtils.water)

        new_filename = ImageUtils.generate_filename(f'{original_filename}.{file_suffix}', ImageUtils.pattern,
                                                    ImageUtils.auto_increment)

        url = "https://sm.ms/api/v2/upload"
        headers = {'Authorization': ImageUtils.smms_token}
        files = {'smfile': (new_filename, watermarked_image_io)}

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if response.status_code == 200 and result['success']:
            return original_filename, result['data']['url'], result['data']['delete']
        else:
            raise Exception(f"Upload to SMMS failed: {result.get('message', 'Unknown error')}")

    @staticmethod
    def upload_to_smms(image_path, water, token, pattern, auto_increment):
        """
        上传本地文件到smms图床，期间需要格式化文件名，添加水印

        :param image_path: 本地图片路径
        :param water: 水印文本
        :param token: smms_token
        :param token: smms_token
        :param pattern: 文件名格式化模板
        :param auto_increment: 自增序列
        :return: (原文件名, imgURL)
        """
        # 添加水印
        watermarked_image = ImageUtils.add_watermark(image_path, water)

        # 获取原文件名去掉后缀部分
        original_filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        new_filename = ImageUtils.generate_filename(image_path.rsplit('/', 1)[-1], pattern, auto_increment)

        url = "https://sm.ms/api/v2/upload"
        headers = {'Authorization': token}
        files = {'smfile': (new_filename, watermarked_image)}

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if response.status_code == 200 and result['success']:
            return original_filename, result['data']['url'], result['data']['delete']
        else:
            raise Exception(f"Upload to SMMS failed: {result.get('message', 'Unknown error')}")

    @staticmethod
    def upload_to_imgurl_image(image_path):
        """
        上传本地文件到imgURL图床，期间需要格式化文件名，添加水印

        :param image_path: 本地图片路径
        :return: (原文件名, imgURL)
        """
        # 添加水印
        watermarked_image = ImageUtils.add_watermark(image_path, ImageUtils.water)
        filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        url = "https://www.imgurl.org/api/v2/upload"
        files = {'file': (image_path.rsplit('/', 1)[-1], watermarked_image)}
        data = {'uid': ImageUtils.imgURL_uid, 'token': ImageUtils.imgURL_token, 'album_id': ImageUtils.imgURL_album_id}

        response = requests.post(url, files=files, data=data)
        result = response.json()

        if response.status_code == 200 and result['code'] == 200:
            return filename, result['data']['url']
        else:
            raise Exception(f"Upload to ImgURL failed: {result.get('message', 'Unknown error')}")

    @staticmethod
    def upload_to_imgurl(image_path, water, album_id, uid, token):
        """
        上传本地文件到imgURL图床，期间需要格式化文件名，添加水印

        :param image_path: 本地图片路径
        :param water: 水印文本
        :param album_id: 相册 id
        :param uid: imgURL_uid
        :param token: imgURL_token
        :return: (原文件名, imgURL)
        """
        # 添加水印
        watermarked_image = ImageUtils.add_watermark(image_path, water)
        filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        url = "https://www.imgurl.org/api/v2/upload"
        files = {'file': (image_path.rsplit('/', 1)[-1], watermarked_image)}
        data = {'uid': uid, 'token': token, 'album_id': album_id}

        response = requests.post(url, files=files, data=data)
        result = response.json()

        if response.status_code == 200 and result['code'] == 200:
            return filename, result['data']['url']
        else:
            raise Exception(f"Upload to ImgURL failed: {result.get('message', 'Unknown error')}")

    @staticmethod
    def upload_images_to_smms_from_directory(parent_path: str):
        success_results = {}
        failed_results = []
        allowed_formats = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}

        # 遍历目录中的所有文件
        for root, dirs, files in os.walk(parent_path):
            for file in files:
                # 只处理图片文件
                if file.split('.')[-1].lower() in allowed_formats:
                    file_path = os.path.join(root, file)
                    original_filename: str = ''
                    # 调用 upload_to_smms 方法上传图片
                    try:
                        original_filename, imgURL, deleteUrl = ImageUtils.upload_to_smms_image(file_path)
                        success_results[original_filename] = imgURL  # 将结果存储到字典中
                    except Exception as e:
                        failed_results.append((original_filename, file_path))
                        print(f'图片上传失败：{original_filename}---->{file_path}---->{e}')
        return (success_results, failed_results)

    @staticmethod
    def upload_images_to_imgURL_from_directory(parent_path: str):
        success_results = {}
        failed_results = []
        allowed_formats = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}

        # 遍历目录中的所有文件
        for root, dirs, files in os.walk(parent_path):
            for file in files:
                # 只处理图片文件
                if file.split('.')[-1].lower() in allowed_formats:
                    file_path = os.path.join(root, file)
                    original_filename: str = ''
                    # 调用 upload_to_imgurl 方法上传图片
                    try:
                        original_filename, imgURL = ImageUtils.upload_to_imgurl_image(file_path)
                        success_results[original_filename] = imgURL  # 将结果存储到字典中
                    except Exception as e:
                        failed_results.append((original_filename, file_path))
                        print(f'图片上传失败：{original_filename}---->{file_path}---->{e}')

        return (success_results, failed_results)


class DataUtils:

    @staticmethod
    def output_data_to_xlsx(headers: List[str], data: List, file_name: str):
        try:
            wb = openpyxl.load_workbook(file_name)
            ws = wb.active
        except FileNotFoundError:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Data"
            ws.append(headers)  # 写入表头
        # 将数据追加到Excel文件中
        ws.append(data)
        wb.save(file_name)  # 保存Excel文件

    @staticmethod
    def decode_bytes(obj):
        if isinstance(obj, dict):
            return {DataUtils.decode_bytes(k): DataUtils.decode_bytes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DataUtils.decode_bytes(i) for i in obj]
        elif isinstance(obj, tuple):
            return tuple(DataUtils.decode_bytes(i) for i in obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')
        else:
            return obj

class FileUtils:

    @staticmethod
    def clear_directory(directory_path: str):
        # 检查文件夹是否存在
        if os.path.exists(directory_path):
            # 删除整个目录及其子目录
            shutil.rmtree(directory_path)
            # 重新创建空目录
            os.makedirs(directory_path)
            print(f"目录 {directory_path} 已清空")
        else:
            print(f"目录 {directory_path} 不存在")

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

# 主程序
def import_aticle():
    base_image_path = r'C:\Users\Administrator\Desktop\image'
    file_path = r'C:\Users\Administrator\Desktop\wordpress_articles.xlsx'
    field_mapping = {
        '标题': 'title',
        '封面': 'image',
        '内容': 'content',
        '发布状态': 'status',
        '标签': 'tags',
        '分类': 'category',
        '价格': 'cao_price',
        '资源链接': 'source_url',
        '提取码': 'pwd'
    }
    # 读取 xlsx 文件，映射到 article_meta
    article_metas: List[ArticleMeta] = WordpressUtils.read_xlsx_to_article_metas(file_path, field_mapping)
    # 将 article_meta 映射到 article，将上传成功的imgURL填充到 image 中
    articles: List[Article] = WordpressUtils.article_metas_to_articles(base_image_path, article_metas)
    # 发布文章
    WordpressUtils.post_articles(articles)
    # 清空 image 文件夹
    # FileUtils.clear_directory(base_image_path)
    input('\n\n回车结束程序（enter）')


def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")


if __name__ == "__main__":
    enable_proxy()
    import_aticle()
