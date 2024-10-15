import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# 定义URL
url = 'https://bbs.abab9.cn/2024/10/14/267752/'

# 使用urlparse解析URL
parsed_url = urlparse(url)
path = parsed_url.path  # 获取URL的路径

# 定义请求头
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'wordpress_logged_in_b8a556d26254189b46ca27506ee3d0e7=21zys%7C1730125460%7CcdugIbXSf65XM4wFmXWa1gvGSDjyS7c1DB5x5BpZSIq%7Cd3a41d1648a283a1e498c52bfd1d606df13d18acd4ac1297a05bb8e0c515df91',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

# 发送GET请求
response = requests.get(url, headers=headers)

# 检查请求是否成功
if response.status_code == 200:
    print("请求成功，解析HTML内容...")
    # 解析HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # 打印HTML的标题
    title = soup.title.string if soup.title else "无标题"
    print("网页标题:", title)

    # 示例：打印网页中的所有链接
    for link in soup.find_all('a'):
        print(link.get('href'))
else:
    print(f"请求失败，状态码: {response.status_code}")
