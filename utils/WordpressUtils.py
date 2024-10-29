import json

from wordpress_xmlrpc import Client, WordPressPost, ServerConnectionError
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods import taxonomies
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Union, Set, Dict
import phpserialize, random, os, collections
from .RedisUtils import RedisUtils
from .ImageUtils import ImageUtils
from .FileUtils import FileUtils
from .DataUtils import DataUtils
from .LogUtils import LogUtils
from datetime import datetime
from .OpenAIUtils import OpenAIUtils, Prompt

# 添加 Iterable 到 collections 模块
collections.Iterable = collections.abc.Iterable

class Article:
    title: str = None
    content: str = None
    date: datetime = None
    post_status: str = None
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
    series: str = ''
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
            return str(self.tags).replace('，', ',').replace(',,', ',').strip(',').split(',')
        return []

    def get_category(self):
        if self.category != '':
            return self.category.replace('，', ',').replace(',,', ',').strip(',').split(',')
        return []

    def get_series(self):
        if self.series != '':
            return str(self.series).replace('，', ',').replace(',,', ',').strip(',').split(',')

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
            return str(self.pwd)
        return ''

    def get_cao_paynum(self):
        if self.cao_paynum:
            return str(self.cao_paynum)
        return str(random.randint(100, 300))


class WordpressUtils:
    __url: str = r'https://res.21zys.com/xmlrpc_Mh359687...php'
    __username: str = '21zys'
    __password: str = 'Mh359687..'
    __client = None

    @classmethod
    def client(cls,
               url: str = r'https://res.21zys.com/xmlrpc_Mh359687...php',
               username: str = '21zys',
               password: str = 'Mh359687..') -> Client:
        if not all((url == cls.__url, username == cls.__username, password == cls.__password)) or cls.__client is None:
            cls.__url = url
            cls.__username = username
            cls.__password = password
            cls.__client = Client(cls.__url, cls.__username, cls.__password)
        return cls.__client

    @classmethod
    def get_all_tag_name(cls) -> Set[str]:
        """
        获取 wordpress 中所有的标签

        :return: set(str)
        """
        return {tag.name for tag in cls.client().call(taxonomies.GetTerms('post_tag'))}

    @classmethod
    def get_all_post(cls, number=100, offset=0, limit=0) -> List[WordPressPost]:
        """
        获取 wordpress 中所有的文章

        :param number: 需要获取多少篇文章，超过则停止
        :param offset: 跳过多少篇文章
        :param limit: 页面大小
        :return: WordPressPost 文章列表
        """
        all_posts = []
        while True:
            try:
                # 获取一部分文章，使用 offset 和 number 控制
                posts = cls.client().call(GetPosts({'number': number, 'offset': offset}))
                if not posts:
                    break  # 如果没有返回文章，说明已经获取完毕
                all_posts.extend(posts)
                if limit != 0 and len(all_posts) >= limit:
                    break
                offset += number  # 更新 offset，以便获取下一部分文章
            except ServerConnectionError as e:
                LogUtils.error(f"Connection error: {e}")
                break
            except Exception as e:
                LogUtils.error(f"An error occurred: {e}")
                break
        return all_posts

    @classmethod
    def post_article(cls, article: Article, is_duplicate: bool = False) -> Union[int, None]:
        """
        发布文章

        :param article: Article 类型的文章
        :param is_duplicate: 是否允许重复文章（根据文章标题判断）
        :return: postId、None
        """
        try:
            post = WordPressPost()
            post.title = article.title
            if article.date:
                post.date = article.date
                post.date_modified = article.date
            post.content = article.content
            post.post_status = article.post_status
            post.terms_names = article.terms_names
            post.custom_fields = article.custom_fields
            post.comment_status = 'open'
            post.id = cls.client().call(NewPost(post))
            if not is_duplicate and article.post_status == 'publish':
                RedisUtils.add_set(RedisUtils.res_21zys_com_titles, article.title)
            return post.id
        except Exception as e:
            LogUtils.error(f"发布文章失败：{e}")
        return None


    @classmethod
    def post_articles(cls, articles: List[Article], is_duplicate: bool = False) -> List[int]:
        """
        批量发布文章

        :param article: Article 类型的文章
        :param is_duplicate: 是否允许重复文章
        :return: postId 数组
        """
        total = len(articles)
        zfill_size = len(str(total))
        index = 1
        post_ids = []
        for article in articles:
            LogUtils.info(f"{str(index).zfill(zfill_size)}/{total}-->正在发布：{article.title}")
            index += 1
            post_id = cls.post_article(article, is_duplicate)
            if post_id:
                post_ids.append(post_id)

        return post_ids

    @classmethod
    def __read_xlsx_to_article_metas(cls, file_path: str, field_mapping: Dict[str, str]) -> List[ArticleMeta]:
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

    @classmethod
    def article_metas_to_articles(cls, base_image_path: str, article_metas: List[ArticleMeta], has_cover: bool = True):
        """
        将 wordpress xlsx文件模版转为 List[Article]
        :param base_image_path: 本地图片文件路径
        :param article_metas: wordpress_xlsx模版读取的 List[ArticleMeta]
        :return: List[Article]
        """
        articles: List[Article] = []
        tag_names = cls.get_all_tag_name()
        post_titles = RedisUtils.get_set(RedisUtils.res_21zys_com_titles)
        if not post_titles:
            post_titles = {post.title for post in cls.get_all_post()}
            RedisUtils.add_set(RedisUtils.res_21zys_com_titles, *post_titles)
        total = len(article_metas)
        zfill_size = len(str(total))
        index = 1
        for article_meta in article_metas:
            # 判断文章是否需要发布
            if article_meta.title in post_titles or article_meta.get_status() == 'undo':
                LogUtils.info(f'{str(index).zfill(zfill_size)}/{total}-->已存在同名文章或未发布文章，跳过发布，请手动处理：{article_meta.title}')
                index += 1
                continue
            article = Article()
            imgurl = ''
            # 处理封面上传到 sm.ms 图床，调用本地代理 http://localhost:10809
            while not imgurl and article_meta.get_status() == 'publish' and has_cover:
                try:
                    if article_meta.image and article_meta.image != '无':
                        if 'cdn.sa.net' in article_meta.image or 'loli.net' in article_meta.image or 's3.bmp.ovh' in article_meta.image or 's3.uuu.ovh' in article_meta.image:
                            imgurl = article_meta.image
                        else:
                            filename, imgurl, _ = ImageUtils.upload_to_smms_by_image_url(article_meta.image, article_meta.title, use_local=True)
                    else:
                        image_path = ImageUtils.find_first_image_with_text(base_image_path, article_meta.title)
                        if image_path:
                            _, imgurl, deleteUrl = ImageUtils.upload_to_smms_image(image_path, use_local=True)
                        else:
                            LogUtils.info(f'{str(index).zfill(zfill_size)}/{total}-->图片上传失败，请手动处理：{article_meta.title}')
                            index += 1
                            break
                except Exception as e:
                    LogUtils.info(f'上传图片失败：{e}')
            LogUtils.info(f'{str(index).zfill(zfill_size)}/{total}-->{article_meta.title}, {imgurl}')
            # 文章标题
            article.title = article_meta.title
            post_titles.add(article.title)
            # 文章内容
            if has_cover:
                article.content = f"<img class='aligncenter' src='{imgurl}'>\n\n{article_meta.content}"
            else:
                article.content = article_meta.content
            # 文章发布状态
            article.post_status = article_meta.get_status()
            # 自动添加标签
            tag_names.update(article_meta.get_tags())
            tags = {tag_name for tag_name in tag_names if tag_name in article_meta.content or tag_name in article_meta.title}
            tags.update(article_meta.get_tags())
            # 文章 terms:{post_tag,category,series}
            terms_names = {'post_tag': list(tags), 'category': article_meta.get_category(), 'series': article_meta.get_series()}
            article.terms_names = terms_names
            # 资源下载地址拼接
            cao_downurl_new = []
            for idx, value in enumerate(article_meta.source_url.replace("，", ",").split(',')):
                cao_downurl_new.append({
                    'name': article_meta.source_name,
                    'url': value,
                    'pwd': ""
                })
            if article_meta.get_cao_pwd():
                for idx, value in enumerate(article_meta.get_cao_pwd().replace("，", ",").split(",")):
                    cao_downurl_new[idx]['pwd'] = value
            # Ripro-v5 自定义 SEO 关键字
            keywords = []
            keywords.extend(article_meta.get_tags())
            keywords.extend(article_meta.get_category())
            keyword = ','.join(keywords)
            description = f"{BeautifulSoup(article_meta.content, 'html.parser').get_text(strip=True)} \n 自定义关键词：{keyword}"
            # 使用 openai 做文章 seo（description，keyword）
            if description:
                ai_content = OpenAIUtils.client().chat_with_prompt('gpt-4o-mini', description, Prompt.SEO)['content']
                content = json.loads(ai_content)
                description = content['description']
                keyword = content['keyword']
            custom_fields = [
                {'key': 'cao_price', 'value': article_meta.cao_price},                              # Ripro-v5 文章价格
                {'key': 'cao_vip_rate', 'value': article_meta.cao_vip_rate},                        # Ripro-v5 会员折扣
                {'key': 'cao_is_boosvip', 'value': article_meta.get_cao_is_bossvip()},              # Ripro-v5 永久会员是否免费
                {'key': 'cao_close_novip_pay', 'value': article_meta.get_cao_close_novip_pay()},    # Ripro-v5 普通用户禁止购买
                {'key': 'cao_paynum', 'value': article_meta.get_cao_paynum()},                      # Ripro-v5 已售数量
                {'key': 'cao_status', 'value': article_meta.get_cao_status()},                      # Ripro-v5 是否启用付费下载模块
                {'key': 'cao_downurl_new', 'value': cao_downurl_new},                               # Ripro-v5 资源下载地址
                {'key': 'cao_info', 'value': article_meta.cao_info},                                # Ripro-v5 资源其他信息
                {'key': 'cao_demourl', 'value': article_meta.cao_demourl},                          # Ripro-v5 资源预览地址
                {'key': 'cao_diy_btn', 'value': article_meta.cao_diy_btn},                          # Ripro-v5 自定义按钮
                {'key': 'cao_video', 'value': article_meta.cao_video},                              # Ripro-v5 是否启用付费音频模块
                {'key': 'cao_is_video_free', 'value': article_meta.cao_is_video_free},              # Ripro-v5 是否免费播放
                {'key': 'video_url_new', 'value': article_meta.video_url_new},                      # Ripro-v5 媒体播放地址
                {'key': 'post_titie', 'value': article_meta.title},                                 # Ripro-v5 自定义 SEO 标题
                {'key': 'keywords', 'value': keyword},                                              # Ripro-v5 自定义 SEO 关键字
                {'key': 'description', 'value': description},                                       # Ripro-v5 自定义 SEO 描述
                {'key': 'views', 'value': str(random.randint(300, 500))}                            # Ripro-v5 自定义文章浏览数
            ]
            article.custom_fields = custom_fields
            articles.append(article)
            index += 1
        return articles

    @classmethod
    def import_article(cls, has_cover: bool = True) -> None:
        """
        读取 wordpress_articles.xlsx 文件，发布到 wordpress
        :return: None
        """
        cwd = os.getcwd()
        base_image_path = os.path.join(cwd, 'image')
        file_path = os.path.join(cwd, 'file', 'wordpress_articles.xlsx')
        field_mapping = {
            '标题': 'title',
            '封面': 'image',
            '内容': 'content',
            '发布状态': 'status',
            '标签': 'tags',
            '分类': 'category',
            '专题': 'series',
            '价格': 'cao_price',
            '资源链接': 'source_url',
            '提取码': 'pwd'
        }
        # 读取 xlsx 文件，映射到 article_meta
        article_metas: List[ArticleMeta] = cls.__read_xlsx_to_article_metas(file_path, field_mapping)
        # 将 article_meta 映射到 article，将上传成功的imgURL填充到 image 中
        articles: List[Article] = cls.article_metas_to_articles(base_image_path, article_metas, has_cover=has_cover)
        # 发布文章
        cls.post_articles(articles)
        # 清空 image 文件夹
        # FileUtils.clear_directory(base_image_path)
        input('\n\n回车结束程序（enter）')

    @classmethod
    def outport_article(cls, number=100, offset=0, limit=0):
        """
        导出 wordpress 文章到 xlsx 文件中
        :param number:
        :param offset:
        :param limit:
        :return:
        """
        posts: List[WordPressPost] = cls.get_all_post(number, offset, limit)
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
            cao_downurl_new = None
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
                        xlsx_file = os.path.join(os.getcwd(), 'file', 'wordpress_articles_output.xlsx')
                        FileUtils.append_to_excel(xlsx_file, (title, ','.join(categories), url), ('title', 'categories', 'url'))
