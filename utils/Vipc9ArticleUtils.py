import os.path
from typing import List
from .FileUtils import FileUtils
from .RequestUtils import RequestUtils
from .LogUtils import LogUtils
from .ImageUtils import ImageUtils
from bs4 import BeautifulSoup

class Vipc9ArticleUtils:

    @classmethod
    def vipc9_article_collect(cls,
                              link_file_path: str = os.path.join(os.getcwd(), 'file', 'un_publish_articles.txt'),
                              xlsx_file_path: str = os.path.join(os.getcwd(), 'file', 'vipc9_article_collect.xlsx'),
                              open_proxy: bool = True,
                              use_local: bool = False) -> List[tuple]:
        links = FileUtils.read_lines(link_file_path, True)
        result: List[tuple] = []
        index = 0
        total = len(links)
        zfill_len = len(str(total))
        for link in links:
            index += 1
            # 请求页面内容
            html_content = RequestUtils.get(link, open_proxy=open_proxy, use_local=use_local)

            # 解析HTML
            soup = BeautifulSoup(html_content.text, 'html.parser')

            # 获取标题
            title = soup.select_one('header.article-header h1.article-title').get_text(strip=True)
            LogUtils.info(f"正在处理{str(index).zfill(zfill_len)}/{total}-->URL: {link}-->Title: {title}")
            # 获取上传时间
            upload_time = soup.select_one('header.article-header div.article-meta span').get_text(strip=True)
            tags = soup.select_one("div.article-meta").find_all("span")[2].get_text(strip=True).replace('&', ',')
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
                    upload_name, processed_src, delete_url = ImageUtils.upload_to_smms_by_image_url(original_src, title, open_proxy=open_proxy, use_local=use_local)
                    img_tag['src'] = processed_src

            # 返回处理后的内容
            processed_content = soup_content.decode_contents()
            FileUtils.append_to_excel(xlsx_file_path, (link, title, processed_content, tags, upload_time), ("Link", "Title", "Content", "Tags", "UploadTime"))
            result.append((link, title, processed_content, tags, upload_time))
        return result
