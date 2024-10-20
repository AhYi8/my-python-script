import hashlib

class StringUtils:
    @classmethod
    def generate_md5_hash(cls, input_string):
        """
        生成给定字符串的MD5哈希值。

        参数:
        input_string (str): 需要被哈希的字符串。

        返回:
        str: 字符串的MD5哈希值。
        """
        if not isinstance(input_string, str):
            raise ValueError("输入必须是字符串类型")

        # 创建md5对象
        m = hashlib.md5()
        # 更新md5对象以添加字符串的字节表示形式
        m.update(input_string.encode('utf-8'))
        # 获取16进制的哈希值
        return m.hexdigest()