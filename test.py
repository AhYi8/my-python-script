import os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def enable_proxy():
    os.environ['http_proxy'] = 'http://localhost:10809'
    os.environ['https_proxy'] = 'http://localhost:10809'
    print("全局代理已开启")

def get_redirect_url(initial_url:str):
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    service = Service(r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')  # 替换为ChromeDriver的实际路径
    # 创建浏览器实例
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        # 访问指定的中转页面
        driver.get(initial_url)
        # 等待5秒
        time.sleep(5)
        # 获取当前URL（跳转后的网址）
        return driver.current_url
    finally:
        driver.quit()  # 关闭浏览器



# 示例使用
if __name__ == "__main__":
    url = "http://666888.best/2024/09/27/c069b7d93eaccaf1cde5a65fc5a68bb1.html"  # 中转页面链接
    enable_proxy()
    redirect_url = get_redirect_url(url)
    print(f"跳转后的URL: {redirect_url}")