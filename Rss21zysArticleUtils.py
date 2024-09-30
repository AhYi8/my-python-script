import requests, os, time
from bs4 import BeautifulSoup
from typing import List

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


class Rss21zysArticleUtils:
    base_url = "http://rss.21zys.com/api/query.php"
    user = "root"
    t = "4P8iZqrjkZbpJgHxosruQF"
    t = {
        "VIP资源共享": "6GzJ8wNOX3brl010Mk7uPU"
    }
    nb = 1000  # 每页记录数

    @staticmethod
    def fetch_url(base_url: str, params: map, retries: int = 5, delay: int = 2):
        """获取页面内容，并在失败时进行重试，最多重试 `retries` 次，每次重试间隔 `delay` 秒"""
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()  # 如果响应状态码不是200，抛出异常
                return response.content
            except requests.RequestException as e:
                if attempt < retries:
                    time.sleep(delay)  # 等待几秒钟再重试
                else:
                    return None

    @staticmethod
    def output_articles(output_file: str = os.path.join(os.getcwd(), 'file', 'rss_21zys_com_output.txt')):
        params = {
            'user': Rss21zysArticleUtils.user,
            't': Rss21zysArticleUtils.t['VIP资源共享'],
            'f': 'html',
            'nb': Rss21zysArticleUtils.nb,
            'offset': 0
        }
        tg_links = set()
        while(True):
            html_content = Rss21zysArticleUtils.fetch_url(Rss21zysArticleUtils.base_url, params)
            soup = BeautifulSoup(html_content, 'html.parser')
            # 找到所有class='flux'的div
            flux_divs = soup.find_all('div', class_='flux')
            if len(flux_divs) == 0:
                break
            # 遍历div中的a标签
            for div in flux_divs:
                for a_tag in div.find_all('a', href=True):
                    href = a_tag['href']
                    # 如果链接包含tg.me，则保存到集合中
                    # if "https://t.me" in href:
                    tg_links.add(href)
            params['offset'] += Rss21zysArticleUtils.nb
        FileUtils.write_file(output_file, tg_links)


def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")

if __name__ == "__main__":
    enable_proxy()
    Rss21zysArticleUtils.output_articles()
