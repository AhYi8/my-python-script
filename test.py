import requests, os
from bs4 import BeautifulSoup

class FileUtils:
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


class Vipc9Utils:

    @staticmethod
    def fetch_url(url):
        """请求页面并返回HTML内容"""
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        return response.content

    @staticmethod
    def get_article_meta(url):
        """提取文章标题、上传时间和内容"""
        # 请求页面内容
        html_content = Vipc9Utils.fetch_url(url)

        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 获取标题
        title = soup.select_one('header.article-header h1.article-title').get_text(strip=True)

        # 获取上传时间
        upload_time = soup.select_one('header.article-header div.article-meta span').get_text(strip=True)

        # 获取文章内容的div标签
        content_div = soup.select_one('main.site-main div.entry-wrapper > div')

        # 替换figure标签中的内容
        for figure in content_div.find_all('figure'):
            img_tag = figure.find('img')
            if img_tag and img_tag.has_attr('data-srcset'):
                src = img_tag['data-srcset']
                # 创建新的img标签
                new_img_tag = soup.new_tag('img', src=src, **{'class': 'aligncenter'})
                figure.replace_with(new_img_tag)  # 替换figure标签

        # 获取div标签内部的所有内容（不包含div标签本身）
        content = ''.join([str(tag) for tag in content_div.contents])

        return title, upload_time, content