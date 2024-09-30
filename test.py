import requests, re, os, time, string, redis
from retrying import retry
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    def write_file(path: str, data_list, mode: str = 'w', encoding: str = 'u8'):
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

    @staticmethod
    def remove_duplicate_logs(log_path: str = os.path.join(os.getcwd(), 'file', 'logs.txt')):
        logs: set = {log for log in FileUtils.read_file(log_path, is_strip=True) if '跳过采集' not in log and '文章不存在' not in log}
        FileUtils.write_file(log_path, logs)
        

links = []
for i in range(9, 2432):
    links.append(f"https://t.me/yunpanshare/{i}")
FileUtils.write_file(os.path.join(os.getcwd(), 'file', 'test.txt'), links)