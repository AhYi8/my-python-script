import time

from selenium import webdriver
# chromedriver_path = r'C:\Users\Gdc\.wdm\drivers\chromedriver\win32\96.0.4664.45\chromedriver.exe'
browser = webdriver.Chrome()


# 设置浏览器大小为全屏
browser.maximize_window()

browser.get("https://www.baidu.com")
print(browser.title)
print(browser.current_url)
print(browser.name)
print(type(browser.page_source))
browser.close()
