import os, shutil, win32com.client, re
from typing import List

class FileUtils:
    @staticmethod
    def copy_files_to_all_subdirs(files_to_copy: List[str], target_dir):
        """
        复制指定文件到指定文件夹及其子孙文件夹下
        :param files_to_copy:
        :param target_dir:
        :return:
        """
        # 遍历目标文件夹及其所有子文件夹
        for root, dirs, files in os.walk(target_dir):
            # 对每个子目录进行操作
            for file_path in files_to_copy:
                # 获取文件名
                file_name = os.path.basename(file_path)
                # 目标路径
                target_path = os.path.join(root, file_name)

                try:
                    # 复制文件
                    shutil.copy(file_path, target_path)
                    print(f"复制文件 {file_name} 到 {target_path}")
                except Exception as e:
                    print(f"复制文件失败 {file_name}: {e}")

    @staticmethod
    def list_files_in_directory(directory_path):
        try:
            # 列出目标文件夹中的所有项目
            items = os.listdir(directory_path)

            # 过滤出文件
            files = [item for item in items if os.path.isfile(os.path.join(directory_path, item))]
            files.sort()
            return files
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    @staticmethod
    def list_dirs_in_directory(directory_path):
        try:
            # 列出目标文件夹中的所有项目
            items = os.listdir(directory_path)

            # 过滤出文件
            dirs = [item for item in items if os.path.isdir(os.path.join(directory_path, item))]

            return dirs
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def delete_files_with_keyword(directory: str, keyword: str):
        """
        递归删除指定目录及其子目录中包含特定关键字的文件.

        :param directory: 目标文件夹路径
        :param keyword: 要搜索的文件名关键字
        """
        for root, dirs, files in os.walk(directory):
            for file in files:
                if keyword in file:  # 检查文件名是否包含关键字
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    except OSError as e:
                        print(f"Error deleting file {file_path}: {e}")

    def rename_images_in_subfolders(folder_path: str):
        # 遍历指定文件夹下的所有子文件夹
        for subdir in os.listdir(folder_path):
            subdir_path = os.path.join(folder_path, subdir)

            # 确保当前路径是一个子文件夹
            if os.path.isdir(subdir_path):
                # 获取子文件夹内的所有文件
                images = [f for f in os.listdir(subdir_path) if
                          f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]

                # 确定编号的位数，位数由图片的数量决定
                num_images = len(images)
                num_digits = len(str(num_images))  # 序号需要的位数

                # 遍历每个图片文件，重命名
                for idx, image in enumerate(images, start=1):
                    old_image_path = os.path.join(subdir_path, image)

                    # 构造新文件名：子文件夹名_序号.扩展名
                    new_image_name = f"{subdir}_{str(idx).zfill(num_digits)}{os.path.splitext(image)[1]}"
                    new_image_path = os.path.join(subdir_path, new_image_name)

                    # 重命名文件
                    os.rename(old_image_path, new_image_path)
                    print(f"Renamed: {old_image_path} -> {new_image_path}")

    # @staticmethod
    # def modify_all_files_properties_in_directory(directory: str, title: str, subject: str, tags: str, comments: str):
    #     try:
    #         # 使用DsoFile的COM对象
    #         dso = win32com.client.Dispatch("DSOFile.OleDocumentProperties")
    #
    #         for root, _, files in os.walk(directory):
    #             for file in files:
    #                 file_path = os.path.join(root, file)
    #
    #                 try:
    #                     # 打开文件以修改其属性
    #                     dso.Open(file_path)
    #
    #                     # 修改文件的摘要属性：标题、主题、标记、备注
    #                     dso.SummaryProperties.Title = title
    #                     dso.SummaryProperties.Subject = subject
    #                     dso.SummaryProperties.Keywords = tags
    #                     dso.SummaryProperties.Comments = comments
    #
    #                     # 保存修改
    #                     dso.Save()
    #                     print(f"已修改文件属性: {file_path}")
    #
    #                 except Exception as e:
    #                     print(f"修改文件属性时出错: {file_path}, 错误: {e}")
    #
    #         dso.Close()
    #
    #     except Exception as e:
    #         print(f"发生错误: {e}")

    @staticmethod
    def coser_picture_folders_rename(main_folder):
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'}

        def get_readable_size(size_in_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_in_bytes < 1024:
                    return f"{size_in_bytes:.2f}{unit}"
                size_in_bytes /= 1024

        folder_list = [os.path.join(main_folder, folder) for folder in os.listdir(main_folder)
                       if os.path.isdir(os.path.join(main_folder, folder))]

        for folder in folder_list:
            page_total = 0
            video_total = 0
            total_size = 0

            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()

                    if file_ext in image_extensions:
                        page_total += 1
                    elif file_ext in video_extensions:
                        video_total += 1

                    total_size += os.path.getsize(file_path)

            size = get_readable_size(total_size)
            folder_name = os.path.basename(folder)
            new_stats = f"[{page_total}P" + (f"{video_total}V" if video_total != 0 else "") + f"-{size}]"
            new_folder_name = re.sub(r"\[\d+.*B]", new_stats, folder_name)
            new_folder_path = os.path.join(os.path.dirname(folder), new_folder_name)
            os.rename(folder, new_folder_path)
            print(f"Renamed '{folder}' to '{new_folder_path}'")

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
    def write_file(path: str, data_list: List[str], mode: str = 'w', encoding: str = 'u8'):
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


def test_copy_files_to_all_subdirs():
    # 指定要复制的文件和目标文件夹
    files_to_copy = [
        r"C:\Users\Administrator\Desktop\21资源站-一个专注全网精品资源的网站。.url",
        r"C:\Users\Administrator\Desktop\必读.txt"
    ]
    target_dir = r"D:\h\柚木"

    # 执行复制操作
    FileUtils.copy_files_to_all_subdirs(files_to_copy, target_dir)


def test_list_files_in_directory():
    directory_path = r'F:\BaiduNetdiskDownload\玉汇压缩包'
    for file in FileUtils.list_files_in_directory(directory_path):
        print(file)


def test_delete_files_with_keyword():
    parent_path = r'D:\h\波萝社'
    keywords = ['1极品福利资源', '嫩模库-分享嫩模福利', '汤不热导航', '网址发布']
    for keyword in keywords:
        FileUtils.delete_files_with_keyword(parent_path, keyword)


def test_rename_images_in_subfolders():
    parent_path = r'D:\h\柚木'
    FileUtils.rename_images_in_subfolders(parent_path)


def test_modify_all_files_properties_in_directory():
    # 示例使用
    target_directory = r"F:\BaiduNetdiskDownload\玉汇\031\yuuhui玉汇 - NO.031 绿意盎然[93P-2.44GB]"     # 需要修改的文件夹路径
    title = r"更多资源：21zys.com或link3.cc/zscc5545"      # 要修改的标题
    subject = r"更多资源：21zys.com或link3.cc/zscc5545"    # 要修改的主题
    tags = r"更多资源：21zys.com或link3.cc/zscc5545"       # 要修改的标记
    comments = r"更多资源：21zys.com或link3.cc/zscc5545"   # 要修改的备注

    FileUtils.modify_all_files_properties_in_directory(target_directory, title, subject, tags, comments)


def test_coser_picture_folders_rename():
    parent_dir = r'F:\BaiduNetdiskDownload\临时文件夹'
    FileUtils.coser_picture_folders_rename(parent_dir)


if __name__ == '__main__':
    test_list_files_in_directory()
