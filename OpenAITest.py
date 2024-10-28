from utils.OpenAIUtils import OpenAIUtils

api_key = "sk-jZsOhotwvcWSjmYklOyNuxsBd4incHIdrdpqVDzJHl1JQkNr"
prompt = r"""You are a professional article SEO optimization master. Your task is to extract a description of about 150 words and 5-7 keywords from the article I provide. Finally, reply to my question in JSON format, structured as follows: {'description': #this is the description, 'keywords': #these are the keywords, separated by commas}. Both the description and keywords must be in Chinese."""
article = r"""
├──01.【目录】【必看】
| ├──课程截图1.jpg 971.30kb
| ├──课程截图2.jpg 407.68kb
| ├──课程截图3.jpg 526.30kb
| ├──课程截图4.jpg 431.11kb
| ├──课程截图5.jpg 545.53kb
| ├──课程截图6.jpg 422.99kb
| └──总目录 火星时代AE-C4D影视包装全能设计师班.jpg 7.07M
├──火星时代AE-C4D影视包装全能设计师班
| ├──火星时代AE-C4D影视包装全能设计师班.z01 19.00G
| ├──火星时代AE-C4D影视包装全能设计师班.zip 18.85G
| ├──解压缩说明.jpg 193.87kb
| └──注意！注意文件是分卷压缩此文件夹全部下载.jpg 171.24kb
├──注意！用winrar解压缩
| └──注意！用winrar解压缩
| | └──注意！用winrar解压缩
└──总目录 火星时代AE-C4D影视包装全能设计师班.jpg 7.07M
"""

result = OpenAIUtils.client(api_key, "https://api.chatanywhere.tech/v1").chat(model="gpt-4o-mini", messages=article, prompt=prompt)

print(result)