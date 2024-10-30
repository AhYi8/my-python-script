import os, re, random, json
from bs4 import BeautifulSoup
from .RequestUtils import RequestUtils
from .LogUtils import LogUtils
from .WordpressUtils import Article, WordpressUtils
from .DateUtils import DateUtils
from .FileUtils import FileUtils
from .RedisUtils import RedisUtils
from typing import Union
from datetime import datetime
from .OpenAIUtils import OpenAIUtils, Prompt

# 配置日志
class Vip91ChuangYeUtils:
    tag_names = WordpressUtils.get_all_tag_name()
    __openai_utils: OpenAIUtils = OpenAIUtils('mh', OpenAIUtils.MODEL['gpt-4o-mini'], prompt=Prompt.ARTICLE_SEO,open_history=False)

    @classmethod
    def publish_vip_91_chuangye_article(cls,
                                        base_url,
                                        cookies,
                                        is_append_xlsx: bool = True,
                                        xlsx_file_path: str = os.path.join(os.getcwd(), "file", "vip_91chuangye_cn.xlsx"),
                                        open_proxy: bool = True,
                                        use_local: bool = False,
                                        https: bool = False,
                                        region: str = None,
                                        openai_seo: bool = False) -> None:
        """
        采集并发布 vip.91chuangye.cn 资源

        :param base_url: 基础网址（具体到某一个分类的网址）
        :param cookies: 当前网站的 cookies
        :param is_append_xlsx: 采集的文章信息，是否追加到 xlsx 文件中
        :param xlsx_file_path: xlsx 文件路径（默认是 ./file/vip_91chuangye_cn.xlsx）
        :param open_proxy: 是否开启代理
        :param use_local: 是否使用本地代理
        :param https: 是否优先使用支持 https 的代理
        :param region: 是否优先选择指定国家代理
        :param openai_seo: 是否调用 OpenAI 进行 SEO 优化
        :return: None
        """
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        page = 1
        # 从 redis 中查询已经采集过的文章链接
        published_article_links = RedisUtils.get_set(RedisUtils.vip_91_article_links)
        flag = True
        # 采集时间范围：前两天的文章
        stop_date = DateUtils.date_to_datetime(DateUtils.add_days(DateUtils.get_current_date(), -2))

        while flag:
            article_metas = []
            results = []
            if page != 1:
                url = f"{base_url}/page/{page}"
            else:
                url = f"{base_url}/"
            LogUtils.info(f"正在采集页面：{url}")
            html_content = RequestUtils.get(url, open_proxy=open_proxy, use_local=use_local, https=https, region=region).text
            if not html_content:
                break  # 如果请求失败，退出循环

            # 解析出文章信息 link, title, cover, category, article_content, source_url, source_pwd, publish_date
            soup = BeautifulSoup(html_content, 'html.parser')

            post_wrapper = soup.find('div', class_='row posts-wrapper scroll')

            item_list = post_wrapper.find_all('div', recursive=False) if post_wrapper else []

            for item in item_list:
                try:
                    # 提取title和link
                    entry_wrapper = item.find('div', class_='entry-wrapper')
                    title_tag = entry_wrapper.find('h2', class_='entry-title').find('a')
                    title = title_tag.text.strip()
                    link = title_tag['href']

                    # 提取cover
                    cover_tag = item.find('div', class_='entry-media').find('img')
                    cover = cover_tag['data-src'] if cover_tag else None

                    # 提取category
                    category_tags = entry_wrapper.find('span', class_='meta-category-dot').find_all('a')
                    category = ",".join(a.text.strip() for a in category_tags)

                    # 提取 publish_date
                    publish_date_tags = entry_wrapper.find('span', class_='meta-date').find('time')
                    publish_date = DateUtils.to_naive(DateUtils.iso_str_to_datetime(
                        publish_date_tags['datetime'])) if publish_date_tags else DateUtils.get_current_datetime()

                    if DateUtils.is_before(publish_date, stop_date):
                        flag = False
                        break

                    if published_article_links and link in published_article_links:
                        continue

                    source_url, source_pwd, article_content = cls.get_vip_91chuangye_content(link, title, cookies, open_proxy=open_proxy, use_local=use_local, https=https, region=region)

                    results.append((link, title, cover, category, article_content, source_url, source_pwd, DateUtils.datetime_to_str(publish_date)))
                    article_metas.append([link, title, cover, category, article_content, source_url, source_pwd, publish_date])
                except Exception as e:
                    LogUtils.error(f"Error processing article: {e}")
                    continue
            # 下一页
            page += 1
            if is_append_xlsx:
                # 将结果追加到xlsx文件中
                headers = ("文章链接", "标题", "封面", "分类", "内容", "资源链接", "提取码", "发布日期")
                FileUtils.append_to_excel(xlsx_file_path, results, headers)

            # 发布 文章
            if article_metas:
                for article_meta in article_metas:
                    link, title, cover, category, content, source_url, source_pwd, publish_date = article_meta
                    if content is None:
                        LogUtils.error(f"{link}-->{title} 内容异常，跳过发布，请手动处理。")
                        continue
                    article: Article = cls.article_meta_article(title, content, category, source_url, source_pwd, publish_date, openai_seo=openai_seo)
                    LogUtils.info(f"正在采集发布：{link}-->{title}")
                    post_id = WordpressUtils.post_article(article, is_duplicate=True)
                    if post_id:
                        RedisUtils.add_set(RedisUtils.vip_91_article_links, link)

    @classmethod
    def get_vip_91chuangye_content(cls,
                                   url: str,
                                   title: str,
                                   cookies: str,
                                   open_proxy: bool = True,
                                   use_local: bool = False,
                                   https: bool = False,
                                   region: str = None
                                   ) -> Union[tuple, None]:
        """
        获取 vip.91chuangye.cn/bbs.abab9.com 文章内容
        :param url: 文章 url
        :param title: 文章标题
        :param cookies: cookies
        :param open_proxy: 是否开启代理
        :param use_local: 是否使用本地代理
        :param https: 是否优先使用支持 https 的代理
        :param region: 是否优先选择指定国家代理
        :return: url, pwd, article_content
        """
        # 自定义请求头
        if 'vip.91chuangye' in url:
            headers = {
                "GET": "/scxm/page/2/ HTTP/1.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Cookie": cookies,
                "Host": "vip.91chuangye.cn",
                "Referer": "https://vip.91chuangye.cn/scxm/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
        elif 'bbs.abab9' in url:
            # 定义请求头
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Cookie': cookies,
                'Priority': 'u=0, i',
                'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            }
        else:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Cookie': cookies,  # 假设 `cookies` 是一样的
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            }

        html_content = RequestUtils.get(url, headers, open_proxy=open_proxy, use_local=use_local, https=https, region=region).text
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            content = soup.find('div', class_='entry-content u-text-format u-clearfix').decode_contents()
            return cls.handle_content(title, content)
        except Exception as e:
            LogUtils.error(f"Error processing article: {e}")
        return None

    @classmethod
    def handle_content(cls, title: str, content: str) -> tuple:
        """
        解析 vip.91chuangye.cn/bbs.abab9.com 文章内容

        :param title: 文章标题
        :param content: 文章 HTML 内容
        :return: url, pwd, article_content
        """
        # 匹配百度网盘链接
        baidu_pattern1 = r'(?:https?://)?\b(e?yun|pan)\.baidu\.com/[sj]/([\w\-]{5,})(?!\.)'
        baidu_pattern2 = r'(?:https?://)?\b(e?yun|pan)\.baidu\.com/(?:share|wap)/init\?surl=([\w\-]{5,})(?!\.)'
        baidu_pattern3 = r'http://pan\.baidu\.com/share/link\?shareid=[0-9]*&amp;uk=[0-9]*'
        url = None
        article_content = None
        try:
            article_content = re.search(r"""([\s\S]*)<div class="ripay-content""", content).group(1).replace(
                """ decoding=\"async\"""", "")
        except Exception as e:
            LogUtils.error(f"{title}：{e}")
        # 检查百度网盘链接
        match = re.search(f"{baidu_pattern1}|{baidu_pattern2}|{baidu_pattern3}", content, re.IGNORECASE)
        if match:
            url = match.group(0)

        pwd_match = re.search(r"\?pwd=(.{4})|提取码.(.{4})", content)
        pwd = pwd_match.group(1) if pwd_match else ""
        return url, pwd, article_content

    @classmethod
    def article_meta_article(cls, title, content: str, category: str, source_url: str, source_pwd: str, publish_date: datetime, openai_seo: bool = False) -> Article:
        """
        将 ArticleMeta 转为 Article

        :param title: 文章标题
        :param content: 文章内容
        :param category: 文章分类
        :param source_url: 资源链接
        :param source_pwd: 提取码
        :param publish_date: 发布日期
        :return: Article
        """
        article = Article()
        article.title = title
        article.content = content.replace(r"<img", r"<img class='aligncenter'")
        article.date = publish_date
        article.post_status = "publish"
        tags = {tag_name for tag_name in cls.tag_names if tag_name in article.content or tag_name in title}
        terms_names = {'post_tag': list(tags), 'category': category.split(",")}
        article.terms_names = terms_names

        cao_downurl_new = [{'name': title, 'url': source_url, 'pwd': source_pwd}]
        keywords = []
        keywords.extend(list(tags))
        keywords.extend(category)
        keyword = ','.join(keywords)
        description = f"{BeautifulSoup(content, 'html.parser').get_text(strip=True)} \n 自定义关键词：{keyword}"
        # 使用 openai 做文章 seo（description，keyword）
        if description and openai_seo:
            assistant_message = cls.__openai_utils.chat(description)
            description_tag = re.search(r"description[:：]\s?(.*)", assistant_message)
            description = description_tag.group(1) if description_tag else description
            keyword_tag = re.search(r"keywords[:：]\s?(.*)", assistant_message)
            keyword = ','.join([item.strip() for item in keyword_tag.group(1).split(',')]) if keyword_tag else keyword
        custom_fields = [
            {'key': 'cao_price', 'value': "99.9"},
            {'key': 'cao_vip_rate', 'value': "0.6"},
            {'key': 'cao_is_boosvip', 'value': "1"},
            {'key': 'cao_close_novip_pay', 'value': 0},
            {'key': 'cao_paynum', 'value': "0"},
            {'key': 'cao_status', 'value': "1"},
            {'key': 'cao_downurl_new', 'value': cao_downurl_new},
            {'key': 'cao_info', 'value': ""},
            {'key': 'cao_demourl', 'value': ""},
            {'key': 'cao_diy_btn', 'value': ""},
            {'key': 'cao_video', 'value': ""},
            {'key': 'cao_is_video_free', 'value': ""},
            {'key': 'video_url_new', 'value': ""},
            {'key': 'post_titie', 'value': ""},
            {'key': 'keywords', 'value': keyword},
            {'key': 'description', 'value': description},
            {'key': 'views', 'value': str(random.randint(300, 500))}
        ]
        article.custom_fields = custom_fields
        return article