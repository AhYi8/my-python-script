import requests, os, logging
from bs4 import BeautifulSoup
from utils.FileUtils import FileUtils
from utils.ImageUtils import ImageUtils
from utils.TgArticleOutput import TgArticleUtils
from utils.WordpressUtils import WordpressUtils
from utils.Rss21zysComUtils import Rss21zysComUtils


class Vipc9Utils:

    @staticmethod
    def fetch_url(url):
        """请求页面并返回HTML内容"""
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        return response.content

    @staticmethod
    def process_src(src):
        """自定义方法处理src属性值"""
        # 示例处理逻辑，可以根据需要替换为实际逻辑
        return src.replace("example", "processed")

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
        content = content_div.decode_contents()

        # 遍历content中的所有img标签并处理src属性
        soup_content = BeautifulSoup(content, 'html.parser')
        for img_tag in soup_content.find_all('img'):
            if img_tag.has_attr('src'):
                original_src = img_tag['src']
                upload_name, processed_src, delete_url = ImageUtils.upload_to_smms_by_image_url(original_src, title)
                img_tag['src'] = processed_src

        # 返回处理后的内容
        processed_content = soup_content.decode_contents()

        return title, upload_time, processed_content


def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")


def test_FileUtils_append_to_excel():
    xlsx_file_path = os.path.join(os.getcwd(), "file", "test.xlsx")
    data = [
        ("test11", "test12", "test13"),
        ("test21", "test22", "test23"),
    ]
    headers = ("header1", "header2", "header3")
    FileUtils.append_to_excel(xlsx_file_path, data, headers)

def test_tg_article_output():
    cwd = os.getcwd()
    ignore_tags = ('剧集', '国产剧', '端游', '真人秀', '剧情', '动画', '动漫', '国漫', '短剧', '蓝光原盘')
    urls_file = os.path.join(cwd, 'file', 'un_publish_articles.txt')
    excel_file = os.path.join(cwd, 'file', 'tg_articles.xlsx')
    image_save_path = os.path.join(cwd, 'image')
    concurrency = None
    # 如果不传递并发度，会自动检测CPU并设置并发数
    TgArticleUtils.tg_article_output(ignore_tags, urls_file, excel_file, image_save_path, concurrency)


def test_tg_article_output():
    cwd = os.getcwd()
    ignore_tags = ('剧集', '国产剧', '端游', '真人秀', '剧情', '动画', '动漫', '国漫', '短剧', '蓝光原盘')
    urls_file = os.path.join(cwd, 'file', 'un_publish_articles.txt')
    excel_file = os.path.join(cwd, 'file', 'tg_articles.xlsx')
    image_save_path = os.path.join(cwd, 'image')
    concurrency = None
    # 如果不传递并发度，会自动检测CPU并设置并发数，**tg默认需要开启代理**
    TgArticleUtils.tg_article_output(ignore_tags, urls_file, excel_file, image_save_path, concurrency)

def test_wordpress_import_article():
    WordpressUtils.import_article()

def test_telegram_source_link_output():
    Rss21zysComUtils.telegram_source_link_output()


if __name__ == "__main__":
    # test_telegram_source_link_output()
    # test_tg_article_output()
    test_wordpress_import_article()