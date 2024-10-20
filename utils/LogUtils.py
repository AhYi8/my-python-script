import os, logging


# 创建日志目录
log_dir = os.path.join(os.getcwd(), 'file')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建一个 FileHandler，并设置编码为 'utf-8'
log_file = os.path.join(log_dir, 'log.txt')
file_handler = logging.FileHandler(log_file, encoding='utf-8')

# 创建一个日志格式器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 将格式器应用于文件处理器
file_handler.setFormatter(formatter)

# 创建一个 StreamHandler 用于输出到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 获取根日志记录器并配置
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # 设置日志级别
logger.addHandler(file_handler)  # 添加文件处理器
logger.addHandler(console_handler)  # 添加控制台处理器

class LoggingUtils:
    @classmethod
    def info(cls, msg, *args, **kwargs):
        logging.info(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        logging.error(msg, *args, **kwargs)