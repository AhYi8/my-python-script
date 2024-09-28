import requests, os
from bs4 import BeautifulSoup

# 文件名，用于保存结果
output_file = r"C:\Users\Administrator\Desktop\links.txt"

# 发送请求的基础URL
base_url = "http://rss.21zys.com/api/query.php"
user = "root"
t = "4P8iZqrjkZbpJgHxosruQF"
nb = 1000  # 每页记录数

# 初始化一个集合保存链接
tg_links = set()


def fetch_links(offset):
    # 构造请求参数
    params = {
        'user': user,
        't': t,
        'f': 'html',
        'nb': nb,
        'offset': offset
    }

    # 发送HTTP请求
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 找到所有class='flux'的div
        flux_divs = soup.find_all('div', class_='flux')

        # 遍历div中的a标签
        for div in flux_divs:
            for a_tag in div.find_all('a', href=True):
                href = a_tag['href']
                # 如果链接包含tg.me，则保存到集合中
                # if "https://t.me" in href:
                tg_links.add(href)
    else:
        print(f"请求失败，状态码: {response.status_code}")


def save_links_to_file():
    # 将集合中的链接写入文件
    with open(output_file, "w") as file:
        for link in tg_links:
            file.write(link + "\n")


def main():
    offset = 0
    while True:
        fetch_links(offset)
        # 如果获取到的结果少于页面大小nb，表示已经到最后一页，退出循环
        if len(tg_links) < (offset + nb):
            break
        offset += nb

    # 保存结果到文件
    save_links_to_file()
    print(f"链接已保存到 {output_file} 文件中")


def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")

if __name__ == "__main__":
    enable_proxy()
    main()
