import os, schedule, time
from utils.Vip91ChuangYeUtils import Vip91ChuangYeUtils
from utils.FileUtils import FileUtils
from utils.LogUtils import LogUtils
from functools import partial

def schedule_publish_task(open_proxy: bool = True, use_local: bool = False, https: bool = False, region: str = None, openai_seo: bool = False):
    # enable_proxy()
    item: str
    url_cookies = [(item.split(": ")[0].strip(), item.split(": ")[1].strip()) for item in
                   FileUtils.read_lines(os.path.join(os.getcwd(), "file", "cookies.txt"), is_strip=True) if
                   not item.startswith("#")]
    for url, cookies in url_cookies:
        Vip91ChuangYeUtils.publish_vip_91_chuangye_article(url, cookies, open_proxy=open_proxy, use_local=use_local, https=https, region=region, openai_seo=openai_seo)


if __name__ == "__main__":
    # 调用静态方法执行操作
    schedule_publish_task(open_proxy=False, use_local=False, https=False, region=None, openai_seo=True)
    
    # 定义每天定时执行的任务
    scheduled_job = partial(schedule_publish_task, open_proxy=False, use_local=False, https=False, region=None, openai_seo=True)
    schedule.every().hour.do(scheduled_job)  # 设置为每小时执行一次
    while True:
        detect_interval = 60 * 60
        schedule.run_pending()  # 检查是否有任务需要执行
        LogUtils.info(f"等待 {detect_interval} 秒，检测数据。")
        time.sleep(detect_interval)  # 暂停n秒