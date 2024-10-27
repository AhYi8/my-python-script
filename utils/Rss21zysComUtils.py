import os.path
from typing import List
from .RequestUtils import RequestUtils
from .FileUtils import FileUtils
from bs4 import BeautifulSoup


class Rss21zysComUtils:
    __base_url: str = "{site_address}/api/query.php?user={user}&t={query_id}&f={content_type}&nb={limit}&offset={offset}"
    __site_address: str = "https://rss.21zys.com"
    __user: str = "root"
    __query_id: str = "4P8iZqrjkZbpJgHxosruQF"
    __content_type: str = "html"
    __limit: int = 100

    @classmethod
    def telegram_source_link_output(cls,
                           file_path: str = os.path.join(os.getcwd(), "file", "un_publish_articles.txt"),
                           site_address: str = None,
                           user: str = None,
                           query_id: str = None,
                           content_type: str = None,
                           limit: str = 100,
                           open_proxy: bool = True,
                           use_local: bool = True) -> List[str]:
        cls.__site_address = site_address if site_address else cls.__site_address
        cls.__user = user if user else cls.__user
        cls.__query_id = query_id if query_id else cls.__query_id
        cls.__content_type = content_type if content_type else cls.__content_type
        cls.__limit = limit if limit else cls.__limit

        offset: int = 0
        result: List[str] = []
        while True:
            url = cls.__base_url.format(site_address=cls.__site_address,
                                        user=cls.__user,
                                        query_id=cls.__query_id,
                                        content_type=cls.__content_type,
                                        limit=cls.__limit,
                                        offset=offset)

            response = RequestUtils.get(url, open_proxy=open_proxy, use_local=True)
            soup = BeautifulSoup(response.text, "html.parser")

            article_divs = soup.find_all('div', class_="flux")
            if not article_divs:
                return result
            for article_div in article_divs:
                link = article_div.find("h1", class_="title").a["href"]
                if "t.me" in link:
                    result.append(link)
                    FileUtils.write_lines(file_path, [link], 'a')

            offset += cls.__limit


if __name__ == "__main__":
    Rss21zysComUtils.TgSourceLinkOutput()
