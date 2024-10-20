import os, piexif, shutil

from PIL import Image, ImageEnhance


class PictureUtils:

    @staticmethod
    def is_image_file(filename):
        """检查文件是否为图片格式"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']
        return os.path.splitext(filename)[1].lower() in image_extensions

    @staticmethod
    def create_thumbnail(image_path, output_path, size=(128, 128)):
        """生成图片缩略图"""
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(output_path)

    @staticmethod
    def create_thumbnail_in_directory(root_dir, overwrite=False, thumb_dir_name="thumbnails", size=(1024, 1024)):
        """处理目录，生成缩略图"""
        # 获取一级子文件夹
        subfolders = [f.path for f in os.scandir(root_dir) if f.is_dir()]

        for subfolder in subfolders:
            print(f"Processing folder: {subfolder}")

            # 如果不覆盖原图，新建压缩文件夹
            if not overwrite:
                thumb_folder = os.path.join(root_dir, thumb_dir_name, os.path.relpath(subfolder, root_dir))
                os.makedirs(thumb_folder, exist_ok=True)

            # 递归处理子文件夹下的所有文件
            for dirpath, _, filenames in os.walk(subfolder):
                for filename in filenames:
                    src_path = os.path.join(dirpath, filename)

                    # 判断是否为图片文件
                    if PictureUtils.is_image_file(filename):
                        if overwrite:
                            # 直接覆盖原图
                            PictureUtils.create_thumbnail(src_path, src_path, size)
                        else:
                            # 保持目录结构，保存到新建的缩略图文件夹
                            rel_path = os.path.relpath(src_path, subfolder)
                            thumb_path = os.path.join(thumb_folder, rel_path)
                            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                            PictureUtils.create_thumbnail(src_path, thumb_path, size)
                    else:
                        # 非图片文件，复制到对应的目录
                        if not overwrite:
                            rel_path = os.path.relpath(src_path, subfolder)
                            dest_path = os.path.join(thumb_folder, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(src_path, dest_path)

    @staticmethod
    def compress_image(image_path, output_path, quality=85, max_size=None):
        """
        压缩单张图片
        :param image_path: 原始图片路径
        :param output_path: 输出图片路径
        :param quality: 压缩质量（百分比）
        :param max_size: 指定压缩到的最大文件大小（字节），如果为 None 则只按质量压缩
        """
        img = Image.open(image_path)

        # 如果图片是 RGBA 模式，转换为 RGB 模式
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        if max_size:
            # 如果有目标大小，逐步减少压缩质量以达到目标大小的130%以下
            for q in range(quality, 10, -5):
                img.save(output_path, 'JPEG', quality=q)
                if os.path.getsize(output_path) <= max_size * 1.3:  # 文件大小不超过目标大小的130%
                    break
        else:
            img.save(output_path, 'JPEG', quality=quality)

    @staticmethod
    def compress_images_in_folder(input_folder: str, quality=85, max_size=None, overwrite=False):
        """
        批量压缩文件夹中的图片
        :param input_folder: 输入文件夹路径
        :param quality: 压缩质量
        :param max_size: 指定压缩到的最大文件大小，单位（KB）
        :param overwrite: 是否覆盖原图
        """
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"指定的文件夹 {input_folder} 不存在")

        # 如果不覆盖原图，创建一个同级的 <input_folder>_compressed_images 文件夹
        if not overwrite:
            parent_dir = os.path.dirname(input_folder)
            folder_name = os.path.basename(input_folder)
            output_folder = os.path.join(parent_dir, f"{folder_name}_compressed_images")

        for root, _, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if overwrite:
                    output_path = file_path  # 覆盖原图
                else:
                    # 计算相对于输入文件夹的路径
                    relative_path = os.path.relpath(root, input_folder)
                    # 在新压缩文件夹下保持相同的目录结构
                    output_dir = os.path.join(output_folder, relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, file)
                if file.lower().endswith(('jpg', 'jpeg', 'png')):
                    # 压缩并保存图片
                    PictureUtils.compress_image(file_path, output_path, quality, max_size)
                    print(f"已压缩图片: {output_path}")
                else:
                    shutil.copy(file_path, output_path)
                    print(f"已复制其他文件到: {output_path}")

    @staticmethod
    def update_images_exif(directory):
        """
        遍历文件夹，修改其中所有图片的EXIF信息
        """
        # 定义要修改的 EXIF 字段
        modify_fields = {
            "ImageDescription": r"更多资源：21zys.com或link3.cc/zscc5545",
            "XPTitle": r"更多资源：21zys.com或link3.cc/zscc5545",
            "XPComment": r"更多资源：21zys.com或link3.cc/zscc5545",
            "XPKeywords": r"更多资源：21zys.com或link3.cc/zscc5545",
            "XPSubject": r"更多资源：21zys.com或link3.cc/zscc5545"
        }

        def to_utf16le_bytes(text):
            """将字符串转换为 UTF-16LE 编码的字节数组"""
            return text.encode('utf-16le') + b'\x00\x00'  # XP 字段以双空字符结束

        def to_utf8_bytes(text):
            """将字符串转换为 UTF-8 编码的字节数组"""
            return text.encode('utf-8')  # 对于 ImageDescription 使用 UTF-8 编码

        # 递归遍历文件夹
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png')):  # 筛选图片格式
                    image_path = os.path.join(root, file)
                    try:
                        # 打开图片
                        img = Image.open(image_path)

                        # 获取图片的EXIF数据
                        exif_data = img.info.get('exif')
                        if exif_data:
                            exif_dict = piexif.load(exif_data)
                        else:
                            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

                        # 修改EXIF中的相关字段
                        exif_dict["0th"][piexif.ImageIFD.ImageDescription] = to_utf8_bytes(
                            modify_fields["ImageDescription"])
                        exif_dict["0th"][piexif.ImageIFD.XPTitle] = to_utf16le_bytes(modify_fields["XPTitle"])
                        exif_dict["0th"][piexif.ImageIFD.XPComment] = to_utf16le_bytes(modify_fields["XPComment"])
                        exif_dict["0th"][piexif.ImageIFD.XPKeywords] = to_utf16le_bytes(modify_fields["XPKeywords"])
                        exif_dict["0th"][piexif.ImageIFD.XPSubject] = to_utf16le_bytes(modify_fields["XPSubject"])

                        # 生成新的EXIF数据并保存回图片
                        exif_bytes = piexif.dump(exif_dict)

                        # 设置增强因子
                        enhancer = ImageEnhance.Sharpness(img)
                        factor = 2.0

                        # 增强图片
                        img_enhanced = enhancer.enhance(factor)

                        # 根据图片格式判断是否需要设置质量参数
                        if img.format == "JPEG":
                            # 对于 JPEG 格式，保存时使用 quality 参数
                            img_enhanced.save(image_path, exif=exif_bytes, quality=img.info.get('quality') if img.info.get('quality') else 100, icc_profile=img.info.get('icc_profile'), dpi=img.info.get('dpi') if img.info.get('dpi') else (100, 100))
                        else:
                            # 对于其他格式（如 PNG），不使用 quality 参数
                            img_enhanced.save(image_path, exif=exif_bytes)
                        print(f"修改成功: {image_path}")

                    except Exception as e:
                        raise e


def test_update_images_exif():
    parent_dir = r'F:\BaiduNetdiskDownload\临时文件夹'
    PictureUtils.update_images_exif(parent_dir)


def test_create_thumbnail_in_directory():
    # image_dir = r'F:\BaiduNetdiskDownload\玉汇'
    image_dir = r'F:\BaiduNetdiskDownload\玉汇'
    PictureUtils.create_thumbnail_in_directory(image_dir, overwrite=False)


# 示例调用
if __name__ == "__main__":
    test_create_thumbnail_in_directory()
