import requests, re, os, time
from typing import Union
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from .RedisUtils import RedisUtils
from .FileUtils import FileUtils
from .ImageUtils import ImageUtils
from .RequestUtils import RequestUtils
from .LogUtils import LogUtils

class ParseTgArticleUtils:
    @staticmethod
    def get_zh_vip_article(params):
        """
        提取 https://t.me/zh_vip 文章信息。该函数主要用于处理和解析包含文章信息的HTML内容或链接，
        从中提取出文章的标题、描述、下载链接和标签等信息。

        :param params: 包含文章信息的HTML内容或链接字符串。
        :return: 返回一个元组，包含文章的标题、描述、下载链接、文件大小和标签字符串。
                 如果无法解析出文章信息，则返回None。
        """
        link_match = re.search(r'https://pan.quark.cn/s/[a-z0-9]{12}', params)
        link = link_match.group(0) if link_match else ''
        soup = BeautifulSoup(params, 'html.parser')
        for br in soup.find_all('br'):
            br.replace_with('\n')
        html_text = soup.get_text(separator='\n', strip=True)
        html_text_match = re.search(r"^(.*)\n(.*)[\s\S]*\n(标签[:：])?(((#\S+) *)*)$", html_text)
        if html_text_match:
            title = TgArticleUtils.sanitize_filename(TgArticleUtils.clean_title(html_text_match.group(1)))
            title_match = re.search(r'^[\[【](.*)[】\]]$', title)
            title = title_match.group(1) if title_match else title
            title = re.sub(r'\s*(\d+)\s*', r'\1', title)
            description = html_text_match.group(2)
            description = re.sub(r'下载链接[:：]', '', description.strip())
            tags = html_text_match.group(4).split('#')
            tags = [tag.strip() for tag in tags if tag.strip() not in TgArticleUtils.tag_remove_keys and tag.strip() not in title and tag.strip() not in description]
            tag = ','.join(tags).strip(',').replace(',,', ',')
            return title, description, link, "N", tag
        return None

    @staticmethod
    def get_other_tg_quark_article(params: str):
        """
        提取 telegram 文章信息。该函数主要用于处理和解析包含文章信息的HTML内容或链接，
        从中提取出文章的标题、描述、下载链接和标签等信息。

        :param params: 包含文章信息的HTML内容或链接字符串。
        :return: 返回一个元组，包含文章的标题、描述、下载链接、文件大小和标签字符串。
                 如果无法解析出文章信息，则返回None。
        """
        title_regex = r'(名称|资源标题|标题|资源名称)[:：]\n*(.+)'
        description_regex = r'(简介|描述|资源描述)[:：]\n*([\s\S]*)(链接[:：])'
        size_regex = r'大小[:：](.+)'
        tag_regex = r'标签[:：](.+)'

        link_match = re.search(r'https://pan.quark.cn/s/[a-z0-9]{12}', params)
        link = link_match.group(0) if link_match else ''
        html_text = BeautifulSoup(params, "html.parser").get_text(strip=False)
        title_match = re.search(title_regex, html_text)
        description_match = re.search(description_regex, html_text)
        size_match = re.search(size_regex, html_text)
        tag_match = re.search(tag_regex, html_text)

        title = TgArticleUtils.sanitize_filename(
            TgArticleUtils.clean_title(title_match.group(2))) if title_match else ''
        title_match = re.search(r'^[\[【](.*)[】\]]$', title)
        title = title_match.group(1) if title_match else title
        title = re.sub(r'\s*(\d+)\s*', r'\1', title)
        description = description_match.group(2).strip() if description_match else ''
        size = size_match.group(1) if size_match else ''
        tags = tag_match.group(1).replace(' ', '').strip('#').split('#') if tag_match else []
        tags = [tag.strip() for tag in tags if tag.strip() not in TgArticleUtils.tag_remove_keys and tag.strip() not in title and tag.strip() not in description]
        tag = ','.join(tags).strip(',').replace(',,', ',')
        return title, description, link, size, tag


class TgArticleUtils:
    get_tg_article_map = {
        'VIP资源共享': ParseTgArticleUtils.get_zh_vip_article,
        'other': ParseTgArticleUtils.get_other_tg_quark_article
    }
    invalid_chars = r'\/:*?"<>|'
    ads_articles = {'TG必备的搜索引擎，极搜帮你精准找到，想要的群组、频道、音乐 、视频'}
    tag_remove_keys = ['中国', '课程', '中国', '教程', '夸克', '夸克网盘', 'quark', '资源', '知识', '学习']
    res_21zys_com_titles = "res_21zys_com_titles"
    exists_titles: set = None

    @classmethod
    def sanitize_filename(cls, title: str) -> str:
        return ''.join([c if c not in cls.invalid_chars else '_' for c in title])

    @classmethod
    def clean_title(cls, title: str) -> str:
        cleaned_title = title.replace('&#xFEFF;', '').replace('\ufeff', '')
        return cleaned_title.strip()

    @classmethod
    def __get_tg_article_content(cls, html_content: str):
        """
        获取 tg 的 author，首图链接，HTML 内容
        :param html_content:
        :return: author, image_url, html_content
        """
        publish_time = author = image_url = content = ''
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            error = soup.find('div', class_="tgme_widget_message_error")
            if error:
                return '', '', 'Post not found', 'None'
            # 3. 获取作者信息
            author = soup.find('div', class_='tgme_widget_message_author').get_text(strip=True)

            # 4. 获取图片链接
            image_url = soup.find('a', class_='tgme_widget_message_photo_wrap')['style']
            image_url = image_url.split('url(')[-1].split(')')[0].strip('"').strip("'")

            # 5. 获取 HTML 内容
            content = soup.find('div', class_='tgme_widget_message_text').decode_contents()
            publish_time = soup.find('time', datetime=True)
            if publish_time:
                publish_time = publish_time.get('datetime')
        except Exception as e:
            pass

        return author, image_url, content, publish_time

    @classmethod
    def __get_tg_article(cls, author: str, html_content: str):
        """
        获取 tg_article 文章的通用接口，调用实现类方法既可以
        :param author: 作者
        :param html_content: html
        :return: (title, content, link, size, tag)
        """
        html_content = re.sub(r'</?br/?>', '\n', html_content)
        author = author if author in cls.get_tg_article_map.keys() else 'other'
        return cls.get_tg_article_map[author](html_content)

    @classmethod
    def process_url(cls, base_url: str, image_save_path: str, ignore_tags: tuple = None, retries: int = 3, delay: int = 2) -> Union[tuple, None]:
        """
        提取单篇 telegram 文章新到 xlsx 文件中

        此方法从指定的 URL 获取页面内容，解析所需的信息（如标题、作者、图片等），
        并将图片保存在本地。它还记录处理状态，并通过重试指定次数来处理异常。

        :param base_url: 要处理的文章页面的基本 URL。
        :param image_save_path: 下载的图片将在本地保存的路径。
        :param ignore_tags: 在处理过程中要忽略的标签元组。如果文章包含这些标签中的任何一个，则跳过处理。
        :param retries: 失败时的重试次数。
        :param delay: 重试之间的延迟（秒）。
        :return: 一个包含提取的文章信息的元组(URL, Author, Success, Title, Image, Description, Status, Tags, Categories, Price, Link, Size, Publish_time)，或者如果处理失败则返回 None。
"""
        cwd = os.getcwd()
        url = f"{base_url}?embed=1&mode=tme"
        author = title = renamed_image = content = link = size = tag = ''
        success_str = '失败'
        logs_path = os.path.join(cwd, 'file', 'logs.txt')

        for attempt in range(1, retries + 1):
            try:
                # 1. Fetch the page content
                # html_content = cls.__fetch_page(url)
                html_content = RequestUtils.get(url, use_local=True).text
                if html_content is None:
                    LogUtils.error(f"TgArticleUtils_无法获取页面内容: {url}")
                    raise Exception(f"无法获取页面内容: {url}")

                # 2. Parse meta tags (image and description)
                author, image_url, html_content, publish_time = cls.__get_tg_article_content(html_content)
                if html_content == 'Post not found':
                    LogUtils.error(f"TgArticleUtils_文章不存在: {url}")
                    return None
                if not image_url or not html_content:
                    LogUtils.error(f"TgArticleUtils_无法解析页面内容: {url}")
                    raise Exception(f"无法解析页面内容: {url}")

                for ads in cls.ads_articles:
                    if ads in html_content:
                        LogUtils.error(f"TgArticleUtils_广告文章，跳过采集: {url}")
                        return None

                # 3. Apply regex to extract information
                result = cls.__get_tg_article(author, html_content)
                if not result:
                    LogUtils.error(f"TgArticleUtils_正则解析失败: {url}")
                    return (base_url, author, success_str, title, renamed_image, content, link, size, tag)

                title, content, link, size, tag = result
                # 过滤指定标签的文章
                if ignore_tags:
                    for ignore_tag in ignore_tags:
                        if ignore_tag in tag:
                            return None

                if not title or not link:
                    LogUtils.error(f"TgArticleUtils_正则解析失败: {url}")
                    return (base_url, author, success_str, title, renamed_image, content, link, size, tag)

                # 4. Download the image
                success = ImageUtils.download_image(image_url, title, image_save_path, use_local=True)
                if not success:
                    LogUtils.error(f"TgArticleUtils_图片下载失败: {url}")
                    raise Exception(f"图片下载失败: {url}")

                success_str = "成功" if success else "失败"
                if cls.exists_titles is None:
                    cls.exists_titles = RedisUtils.get_set(cls.res_21zys_com_titles)
                if cls.exists_titles and title in cls.exists_titles:
                    LogUtils.error(f"TgArticleUtils_文章已发布：{title}，跳过采集：{url}")
                    return None
                # 5. Return all data for appending to Excel
                # URL, Author, Success, Title, Image, Description, Status, Tags, Categories, Price, Link, Size, Publish_time
                if not content:
                    content = title
                return (base_url, author, success_str, title, None, content, '', tag, None, 0, link, size, publish_time)
            except Exception as e:
                LogUtils.error(f"处理 URL {base_url} 时发生错误: {e}")
                if attempt == retries:
                    return None
                else:
                    time.sleep(delay)

    @classmethod
    def tg_article_output(cls, ignore_tags: tuple = None, urls_file: str = None, excel_file: str = None,
                          image_save_path: str = None, concurrency: int = None) -> None:
        """
        从 urls_file 文件中获取 urls，批量提取 telegram 文章新到 xlsx 文件中

        :param ignore_tags: 忽略指定标签的文章
        :param urls_file: url 文件路径
        :param excel_file: 保存文章信息的 xlsx 文件路径
        :param image_save_path: 下载的图片保存到路径（以文章标题命名）
        :param concurrency: 并发处理的线程数
        :return: 无返回值
        """
        cwd = os.getcwd()
        if not image_save_path:
            # image_save_path = os.path.join(cwd, 'image')
            image_save_path = os.path.join(cwd, 'image')
        if not os.path.exists(image_save_path):
            os.makedirs(image_save_path)
        if not excel_file:
            excel_file = os.path.join(cwd, 'file', 'tg_articles.xlsx')
        if os.path.exists(excel_file):
            os.remove(excel_file)
        if not urls_file:
            urls_file = os.path.join(cwd, 'file', 'un_publish_articles.txt')
        urls = FileUtils.read_lines(urls_file, is_strip=True)

        if not urls:
            LogUtils.error("未找到有效的 URL，检查 urls.txt 文件")
            return

        # 自动检测 CPU 核心数，若用户未指定并发度则自动设置为 CPU 核心数的 2 倍
        if concurrency is None:
            cpu_count = os.cpu_count()
            concurrency = cpu_count * 2 if cpu_count else 4  # 保障至少有 4 个并发线程

        LogUtils.info(f"使用 {concurrency} 个并发线程进行处理")

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_url = {executor.submit(cls.process_url, url, image_save_path, ignore_tags): url for url
                             in
                             urls}
            total = len(urls)
            zfill_size = len(str(total))
            index = 1
            headers = ('URL', 'Author', 'Success', 'Title', 'Image', 'Description', 'Status', 'Tags', 'Categories', 'Price', 'Link', 'Size', 'publish_time')
            for future in as_completed(future_to_url):
                result = future.result()
                if result:

                    FileUtils.append_to_excel(excel_file, result, headers)
                    url = future_to_url[future]
                    print(f"{str(index).zfill(zfill_size)}/{total}-->处理完成: {url}")
                index += 1
        input('\n\n回车结束程序（enter）')