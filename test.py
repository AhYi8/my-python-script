import requests, os, logging
from bs4 import BeautifulSoup
from utils.FileUtils import FileUtils
from utils.ImageUtils import ImageUtils
from utils.TgArticleOutput import TgArticleUtils
from utils.WordpressUtils import WordpressUtils
from utils.Rss21zysComUtils import Rss21zysComUtils
from utils.Vipc9ArticleUtils import Vipc9ArticleUtils

def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")

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

def test_wordpress_import_article(has_cover: bool = True):
    WordpressUtils.import_article(has_cover=has_cover)

def test_telegram_source_link_output():
    Rss21zysComUtils.telegram_source_link_output()


def test_vipc9_article_collect():
    Vipc9ArticleUtils.vipc9_article_collect()

if __name__ == "__main__":
    # test_telegram_source_link_output()
    # test_tg_article_output()
    test_wordpress_import_article(has_cover=False)
    # test_vipc9_article_collect()