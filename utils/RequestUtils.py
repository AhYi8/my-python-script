import requests, time
from PIL.ImageChops import offset

from .LogUtils import LogUtils


class RequestUtils:
    __local_proxy = {
        "proxy": r'localhost:10809'
    }

    @classmethod
    def convert_cookie_to_dict(cls, cookie_str: str):
        """
        将字符串类型的cookie转换为requests模块需要的字典格式
        :param cookie_str: 字符串类型的cookie (格式为 "key1=value1; key2=value2; ...")
        :return: 字典类型的cookie
        """
        cookies = {}
        # 通过分号分割各个键值对
        cookie_items = cookie_str.split(';')

        # 遍历每个键值对，去掉空白并将它们添加到字典中
        for item in cookie_items:
            key, value = item.strip().split('=', 1)
            cookies[key] = value

        return cookies
    
    @classmethod
    def get_proxy(cls, use_local: bool = False, https: bool = False, region: str = None) -> dict[str, object]:
        """
        获取代理代理
        :param use_local: 是否使用本地代理
        :param https: 是否支持 https
        :param region: 筛选国家
        :return: {"proxy","https","fail_count","region","anonymous","source","check_count","last_status","last_time"}
        """
        proxy_list = requests.get("http://152.32.175.149:5010/all/").json()
        if https:
            proxy_list_tmp = [proxy for proxy in proxy_list if proxy['https']]
            proxy_list = proxy_list_tmp if proxy_list_tmp else proxy_list
        if region:
            proxy_list_tmp = [proxy for proxy in proxy_list if region in proxy['region']]
            proxy_list = proxy_list_tmp if proxy_list_tmp else proxy_list

        return cls.__local_proxy if use_local else proxy_list[0]

    @classmethod
    def delete_proxy(cls, proxy):
        requests.get("http://152.32.175.149:5010/delete/?proxy={}".format(proxy))

    @classmethod
    def post(cls, url: str, headers: dict = None, retries: int = 30, timeout: int = 10, delay: int = 3, open_proxy: bool = True, use_local: bool = False, **kwargs):
        """
        发送 POST 请求，默认重试1次，设置超时为5秒，重试间隔默认1秒。
        **默认开启代理池访问**

        :param url: 要请求的URL
        :param headers: 请求头信息
        :param retries: 最大重试次数
        :param timeout: 每次请求的超时时间（秒）
        :param delay: 重试之间的延迟时间（秒）
        :param open_proxy: 是否开启代理访问
        :param use_local: 是否使用本地代理
        :return:
        """
        proxy = cls.get_proxy(use_local).get("proxy")
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        if open_proxy:
            kwargs["proxies"] = proxies
        if headers:
            kwargs["headers"] = headers
        kwargs["timeout"] = timeout

        attempt = 0
        while attempt <= retries:
            try:
                # 发送 POST 请求，带有超时处理
                response = requests.post(url, **kwargs)

                # 检查响应状态码是否为2xx，抛出异常则重试
                response.raise_for_status()
                return response

            except requests.Timeout:
                LogUtils.error(f"Timeout fetching URL: {url}, attempt {attempt + 1}")
            except requests.RequestException as e:
                LogUtils.error(f"Error fetching URL: {url}, attempt {attempt + 1}, Error: {e}")

            # 如果重试次数已用完，返回None
            if attempt == retries:
                cls.delete_proxy(proxy)
                return None

            attempt += 1
            if attempt % 3 == 0:
                old_proxy = proxy
                cls.delete_proxy(proxy)
                proxy = cls.get_proxy().get("proxy")
                LogUtils.info(f"当前代理重试 3 次失败，切换代理继续尝试: {old_proxy}-->{proxy}")
                proxies['http'] = f"http://{proxy}"
            # 每次重试之间等待一段时间
            time.sleep(delay)


    @classmethod
    def get(cls, url: str, headers: dict = None, retries: int = 30, timeout: int = 10, delay: int = 3, open_proxy: bool = True, use_local: bool = False, https: bool = False, region: str = None, **kwargs):
        """
        发送 GET 请求，默认重试1次，设置超时为5秒，重试间隔默认1秒。
        **默认开启代理池访问**

        :param url: 要请求的URL
        :param headers: 请求头信息
        :param retries: 最大重试次数
        :param timeout: 每次请求的超时时间（秒）
        :param delay: 重试之间的延迟时间（秒）
        :param open_proxy: 是否开启代理访问
        :param use_local: 是否使用本地代理
        :param https: 是否优先选择支持 https 代理
        :param region: 使用代理池时，指定哪些地域的代理 IP
        :return: 请求成功返回响应内容，否则返回None
        """
        proxy_dict = cls.get_proxy(use_local, https=https, region=region)
        proxy = proxy_dict.get("proxy")

        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        if headers:
            kwargs["headers"] = headers
        if open_proxy:
            kwargs["proxies"] = proxies
            LogUtils.info(f"当前使用代理：proxy: {proxy}，https: {proxy_dict.get('https')}, region: {proxy_dict.get('region')}")
        kwargs["timeout"] = timeout

        attempt = 0
        while attempt <= retries:
            try:
                # 发送 GET 请求，带有超时处理
                response = requests.get(url, **kwargs)

                # 检查响应状态码是否为2xx，抛出异常则重试
                response.raise_for_status()
                return response

            except requests.Timeout:
                LogUtils.error(f"Timeout fetching URL: {url}, attempt {attempt + 1}")
            except requests.RequestException as e:
                LogUtils.error(f"Error fetching URL: {url}, attempt {attempt + 1}, Error: {e}")

            # 如果重试次数已用完，返回None

            if attempt == retries:
                if open_proxy:
                    cls.delete_proxy(proxy)
                return None

            attempt += 1
            if open_proxy and attempt % 3 == 0:
                old_proxy = proxy
                cls.delete_proxy(proxy)
                proxy_dict = cls.get_proxy(use_local, https=https, region=region)
                LogUtils.info(f"当前代理重试 3 次失败，切换代理继续尝试: {old_proxy}-->{proxy_dict.get("proxy")}，https: {proxy_dict.get('https')}, region: {proxy_dict.get('region')}")
                proxies = {
                    "http": f"http://{proxy}",
                    "https": f"http://{proxy}"
                }
            # 每次重试之间等待一段时间
            time.sleep(delay)