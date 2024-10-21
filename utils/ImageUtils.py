import os, requests, hashlib, uuid, random, string
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from PIL.ImageFile import ImageFile
from typing import Union, Tuple
from .RequestUtils import RequestUtils

class ImageUtils:
    smms_token: str = 'tbVH1tVAwadESF2NdCXrr27UuqmGtNCq'
    imgURL_uid: str = 'b77b5646d741207bc920f2fd3daa3490'
    imgURL_token: str = '6e6c36de4eaaf95bd74b280259f18dd7'
    imgURL_album_id: int = 413
    water: str = 'res.21zys.com'
    pattern: str = 'res.21zys.com-{Y}{m}{d}{h}{i}{s}'
    auto_increment: int = 1

    @staticmethod
    def download_image(image_url: str, filename: str, save_path: str, retries: int = 5, open_proxy: bool = True, use_local: bool = False) -> bool:
        """
        下载 image_url 图片到 save_path 路径下
        :param image_url: 互联网图片链接
        :param filename: 保存到本地的文件名
        :param save_path: 保存到本地的路径
        :param retries: 失败重试次数
        :return:
        """
        for attempt in range(retries):
            try:
                ext = os.path.splitext(image_url)[1]
                # TODO 后缀名需要改进，使用 PIL 判断图片的类型
                filename = filename + ext
                image_path = os.path.join(save_path, filename)
                if not os.path.exists(image_path):
                    response = RequestUtils.fetch_url(image_url, open_proxy=open_proxy, use_local=use_local)
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content))
                    img.save(image_path)
                return True
            except Exception as e:
                pass
        return False

    @classmethod
    def find_first_image_with_text(cls, directory, search_string) -> Union[str, None]:
        """
        根据关键字搜索图片
        :param directory: 目标文件夹
        :param search_string: 关键字
        :return: 图片文件路径/None
        """
        for root, _, files in os.walk(directory):
            for file in files:
                if search_string in file and file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    return os.path.join(root, file)
        return None

    @classmethod
    def add_watermark(cls, image_path, watermark_text):
        """
        读取读取指定路径的图片，添加水印文本

        :param image_path: img图片路径
        :param watermark_text: 水印文本
        :return: img 流
        """
        image = Image.open(image_path)
        watermark_image = image.copy()
        draw = ImageDraw.Draw(watermark_image)

        font_size = int(min(image.size) * 0.15)  # 水印字体大小
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)

        # 创建透明图层用于绘制水印
        watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))
        draw_watermark = ImageDraw.Draw(watermark_layer)

        # 计算文本的宽度和高度
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # 计算水印的位置（居中）
        x = (watermark_layer.width - text_width) / 2
        y = (watermark_layer.height - text_height) / 2

        # 设置透明度（255为不透明）
        fill = (0, 0, 0, int(255 * 0.6))  # 黑色，透明度为0.4

        # 添加水印文本
        draw_watermark.text((x, y), watermark_text, font=font, fill=fill)

        # 旋转水印图层45度
        watermark_layer = watermark_layer.rotate(45, expand=True)

        # 创建一个与原始图像尺寸相同的空白图像
        full_watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))

        # 计算旋转后图层的位置以居中对齐
        paste_x = (full_watermark_layer.width - watermark_layer.width) // 2
        paste_y = (full_watermark_layer.height - watermark_layer.height) // 2

        # 将旋转后的水印图层粘贴到空白图像上
        full_watermark_layer.paste(watermark_layer, (paste_x, paste_y), watermark_layer)

        # 将水印图层与原始图像合并
        watermarked_image = Image.alpha_composite(watermark_image.convert('RGBA'), full_watermark_layer)

        watermarked_io = BytesIO()
        watermarked_image.convert('RGB').save(watermarked_io, format=image.format)
        watermarked_io.seek(0)
        return watermarked_io

    @classmethod
    def add_watermark_to_image(cls, image: ImageFile, watermark_text):
        """
        给指定图片添加水印文本

        :param image: 图片文件
        :param watermark_text: 水印文本
        :return:
        """
        watermark_image = image.copy()
        draw = ImageDraw.Draw(watermark_image)

        font_size = int(min(image.size) * 0.15)  # 水印字体大小
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)

        # 创建透明图层用于绘制水印
        watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))
        draw_watermark = ImageDraw.Draw(watermark_layer)

        # 计算文本的宽度和高度
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # 计算水印的位置（居中）
        x = (watermark_layer.width - text_width) / 2
        y = (watermark_layer.height - text_height) / 2

        # 设置透明度（255为不透明）
        fill = (0, 0, 0, int(255 * 0.6))  # 黑色，透明度为0.4

        # 添加水印文本
        draw_watermark.text((x, y), watermark_text, font=font, fill=fill)

        # 旋转水印图层45度
        watermark_layer = watermark_layer.rotate(45, expand=True)

        # 创建一个与原始图像尺寸相同的空白图像
        full_watermark_layer = Image.new('RGBA', watermark_image.size, (0, 0, 0, 0))

        # 计算旋转后图层的位置以居中对齐
        paste_x = (full_watermark_layer.width - watermark_layer.width) // 2
        paste_y = (full_watermark_layer.height - watermark_layer.height) // 2

        # 将旋转后的水印图层粘贴到空白图像上
        full_watermark_layer.paste(watermark_layer, (paste_x, paste_y), watermark_layer)

        # 将水印图层与原始图像合并
        watermarked_image = Image.alpha_composite(watermark_image.convert('RGBA'), full_watermark_layer)

        watermarked_io = BytesIO()
        watermarked_image.convert('RGB').save(watermarked_io, format=image.format)
        watermarked_io.seek(0)
        return watermarked_io

    @classmethod
    def generate_filename(cls, filename: str, pattern: str, auto_increment: int):
        """
        返回格式化的文件名，用于smms上传时的文件名格式化

        :param filename: 原文件名
        :param pattern: 格式化模板
        :param auto_increment: 自增序列
        :return: 格式化后的文件名
        """
        base, ext = filename.rsplit('.', 1)
        now = datetime.now()

        replacements = {
            '{Y}': now.strftime('%Y'),
            '{y}': now.strftime('%y'),
            '{m}': now.strftime('%m'),
            '{d}': now.strftime('%d'),
            '{h}': now.strftime('%H'),
            '{i}': now.strftime('%M'),
            '{s}': now.strftime('%S'),
            '{ms}': now.strftime('%f')[:3],
            '{timestamp}': str(int(now.timestamp())),
            '{md5}': hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
            '{md5-16}': hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16],
            '{uuid}': str(uuid.uuid4()),
            '{str-6}': ''.join(random.choices(string.ascii_letters + string.digits, k=6)),
            '{filename}': base,
            '{auto}': str(auto_increment)
        }

        for key, value in replacements.items():
            pattern = pattern.replace(key, value)

        return pattern + '.' + ext

    @classmethod
    def upload_to_smms_image(cls, image_path: str) -> Union[Tuple[str, str, str], None]:
        """
        上传本地文件到 smms 图床，期间需要格式化文件名，添加水印

        :param image_path: 本地图片路径
        :return: (原文件名, imgURL, deleteURL)
        """
        # 添加水印
        watermarked_image = cls.add_watermark(image_path, cls.water)

        # 获取原文件名去掉后缀部分
        original_filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        new_filename = cls.generate_filename(image_path.rsplit('/', 1)[-1], cls.pattern,
                                             cls.auto_increment)

        url = "https://sm.ms/api/v2/upload"
        headers = {'Authorization': cls.smms_token}
        files = {'smfile': (new_filename, watermarked_image)}

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if response.status_code == 200 and result['success']:
            return original_filename, result['data']['url'], result['data']['delete']
        else:
            raise Exception(f"Upload to SMMS failed: {result.get('message', 'Unknown error')}")
        return None

    @classmethod
    def upload_to_smms_by_image_url(cls, image_url: str, original_filename: str):
        """
        上传网络文件到 smms 图床，期间需要格式化文件名，添加水印

        :param image_url: 本地图片路径
        :return: (原文件名, imgURL, deleteURL)
        """
        # 下载图片
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception("Failed to download image.")

        image = Image.open(BytesIO(response.content))
        try:
            # 获取原始文件名后缀
            file_suffix = image_url.rsplit('/', 1)[-1].rsplit('.', 1)[1]
        except Exception as e:
            file_suffix = 'jpg'

        # 添加水印
        watermarked_image_io = cls.add_watermark_to_image(image, cls.water)

        new_filename = cls.generate_filename(f'{original_filename}.{file_suffix}', cls.pattern,
                                             cls.auto_increment)

        url = "https://sm.ms/api/v2/upload"
        headers = {'Authorization': cls.smms_token}
        files = {'smfile': (new_filename, watermarked_image_io)}

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if response.status_code == 200 and result['success']:
            return original_filename, result['data']['url'], result['data']['delete']
        else:
            raise Exception(f"Upload to SMMS failed: {result.get('message', 'Unknown error')}")

    @classmethod
    def upload_to_smms(cls, image_path: str, water: str, token: str, pattern: str, auto_increment: int):
        """
        上传本地文件到 smms 图床，期间需要格式化文件名，添加水印，显式指定 water、token、pattern、auto_increment

        :param image_path: 本地图片路径
        :param water: 水印文本
        :param token: smms_token
        :param token: smms_token
        :param pattern: 文件名格式化模板
        :param auto_increment: 自增序列
        :return: (原文件名, imgURL, deleteURL)
        """
        # 添加水印
        watermarked_image = cls.add_watermark(image_path, water)

        # 获取原文件名去掉后缀部分
        original_filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        new_filename = cls.generate_filename(image_path.rsplit('/', 1)[-1], pattern, auto_increment)

        url = "https://sm.ms/api/v2/upload"
        headers = {'Authorization': token}
        files = {'smfile': (new_filename, watermarked_image)}

        response = requests.post(url, headers=headers, files=files)
        result = response.json()

        if response.status_code == 200 and result['success']:
            return original_filename, result['data']['url'], result['data']['delete']
        else:
            raise Exception(f"Upload to SMMS failed: {result.get('message', 'Unknown error')}")

    @classmethod
    def upload_to_imgurl_image(cls, image_path: str):
        """
        上传本地文件到 imgURL 图床，期间需要格式化文件名，添加水印

        :param image_path: 本地图片路径
        :return: (原文件名, imgURL)
        """
        # 添加水印
        watermarked_image = cls.add_watermark(image_path, cls.water)
        filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        url = "https://www.imgurl.org/api/v2/upload"
        files = {'file': (image_path.rsplit('/', 1)[-1], watermarked_image)}
        data = {'uid': cls.imgURL_uid, 'token': cls.imgURL_token, 'album_id': cls.imgURL_album_id}

        response = requests.post(url, files=files, data=data)
        result = response.json()

        if response.status_code == 200 and result['code'] == 200:
            return filename, result['data']['url']
        else:
            raise Exception(f"Upload to ImgURL failed: {result.get('message', 'Unknown error')}")

    @classmethod
    def upload_to_imgurl(cls, image_path, water, album_id, uid, token):
        """
        上传本地文件到 imgURL 图床，期间需要格式化文件名，添加水印
        需要显式指定 water，album_id，uid，token

        :param image_path: 本地图片路径
        :param water: 水印文本
        :param album_id: 相册 id
        :param uid: imgURL_uid
        :param token: imgURL_token
        :return: (原文件名, imgURL)
        """
        # 添加水印
        watermarked_image = cls.add_watermark(image_path, water)
        filename = image_path.rsplit('/', 1)[-1].rsplit('.', 1)[0]

        url = "https://www.imgurl.org/api/v2/upload"
        files = {'file': (image_path.rsplit('/', 1)[-1], watermarked_image)}
        data = {'uid': uid, 'token': token, 'album_id': album_id}

        response = requests.post(url, files=files, data=data)
        result = response.json()

        if response.status_code == 200 and result['code'] == 200:
            return filename, result['data']['url']
        else:
            raise Exception(f"Upload to ImgURL failed: {result.get('message', 'Unknown error')}")