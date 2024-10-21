import os, schedule, time
from utils.Vip91ChuangYeUtils import Vip91ChuangYeUtils
from utils.FileUtils import FileUtils
from utils.LogUtils import LogUtils


def schedule_publish_task():
    # enable_proxy()
    item: str
    url_cookies = [(item.split(": ")[0].strip(), item.split(": ")[1].strip()) for item in
                   FileUtils.read_file(os.path.join(os.getcwd(), "file", "cookies.txt"), is_strip=True) if
                   not item.startswith("#")]
    for url, cookies in url_cookies:
        Vip91ChuangYeUtils.publish_vip_91_chuangye_article(url, cookies)


if __name__ == "__main__":
    # 调用静态方法执行操作
    schedule_publish_task()

    # 定义每天定时执行的任务
    schedule.every().hour.do(schedule_publish_task)  # 设置为每小时执行一次
    while True:
        detect_interval = 60 * 60
        schedule.run_pending()  # 检查是否有任务需要执行
        LogUtils.info(f"等待 {detect_interval} 秒，检测数据。")
        time.sleep(detect_interval)  # 暂停n秒