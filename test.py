# script.py

import requests, os, re
from bs4 import BeautifulSoup

os.environ['http_proxy'] = 'http://localhost:10809'
os.environ['https_proxy'] = 'http://localhost:10809'

# 1. 发送 HTTP 请求
url = r'https://t.me/zh_vip/2422?embed=1&mode=tme'  # 替换为目标 URL
response = requests.get(url)

# 2. 解析 HTML
soup = BeautifulSoup(response.content, 'html.parser')

# 3. 获取作者信息
author = soup.find('div', class_='tgme_widget_message_author').get_text(strip=True)

# 4. 获取图片链接
image_url = soup.find('a', class_='tgme_widget_message_photo_wrap')['style']
image_url = image_url.split('url(')[-1].split(')')[0].strip('"').strip("'")

# 5. 获取 HTML 内容
html_content = soup.find('div', class_='tgme_widget_message_text').decode_contents()
soup = BeautifulSoup(html_content, 'html.parser')
for br in soup.find_all('br'):
    br.replace_with('\n')
html_text = soup.get_text(separator='\n', strip=True)
html_text_match = re.search(r"^(.*)\n(.*)[\s\S]*\n(((#\S+) ?)*)$", html_text)
if html_text_match:
    t1 = html_text_match.group(1)
    t2 = html_text_match.group(2)
    t3 = html_text_match.group(3)
    print(t1, t2, t3)
# 6. 输出结果
print(f'Author: {author}')
print(f'Image URL: {image_url}')
print(f'HTML Content: {html_content}')
