import os.path

import openai
import yaml
from openai import OpenAI
from .RequestUtils import RequestUtils
from .LogUtils import LogUtils
from typing import Dict
from itertools import cycle

class ApiKey:
    """
    ApiKey 管理器，从配置文件中读取 api_key 与对应的 base_url，并提供轮询接口
    """
    def __init__(self, config_file: str = os.path.join(os.getcwd(), "file", "api_key.yml")):
        self.config_file = config_file
        self.api_keys = self.load_config()
        self.current_user = None
        self.key_cycles = {}

    def load_config(self) -> Dict:
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def get_api_key(self, username: str) -> Dict:
        if username not in self.api_keys:
            raise ValueError(f"Username {username} not found in config")

        if username != self.current_user:
            self.current_user = username
            self.key_cycles[username] = cycle(self.api_keys[username])

        return next(self.key_cycles[username])

    def rotate_api_key(self) -> Dict:
        if not self.current_user:
            raise ValueError("No current user set")
        return self.get_api_key(self.current_user)

class Prompt:
    CHAT_SYSTEM_CONTENT = "You are a helpful assistant."
    IMAGE_GENERATION_PROMPT = "Create an image based on the following description:"
    ARTICLE_SEO = """#01 You are a professional article SEO optimization master.\n#02 Your task is to extract a description of about 150 words and 5-7 keywords from the article I provide.\n#03 Follow the user’s requirements carefully & to the letter.\n#04 You must respond to my request in the following format, structured as follows: description: #{1}#{2}keyword: #{3}.Among them, #{1} is filled with a description, #{2} is filled with two line breaks, and #{3} is filled with a keyword.\n#05 Ensure that the description and keywords are primarily in Chinese.\n#06 Your description and keywords for the summary must be completely dependent on the article provided by the user.\n#07 If the article provided by the user has too few words, the #02 may not be followed.\n#08 Your responses should be informative and logical.\n#09 You can only give one reply for each conversation turn."""


class OpenAIUtils:
    __api_key: str = None
    __model: str = 'gpt-3.5-turbo'
    __base_url: str = None
    __client: OpenAI = None

    def __init__(self, api_key_manager: ApiKey, username: str, model: str = "gpt-3.5-turbo", prompt: str = Prompt.CHAT_SYSTEM_CONTENT, open_history: bool = True):
        """
        初始化 OpenAiUtils
        :param api_key_manager: api_key 管理器，主要用户轮询 api_key 和 base_url
        :param username: 当前用户
        :param model: 对话模型
        :param prompt: 系统 Prompt
        :param open_history: 是否开启上下文对话
        """
        self.api_key_manager = api_key_manager
        self.username = username
        self.model = model
        self.prompt = prompt
        self.open_history = open_history
        self.conversation_history = []          # 用来保留上下文
        self.setup_client()

    def setup_client(self):
        api_key_data = self.api_key_manager.get_api_key(self.username)
        api_key = api_key_data['api_key']
        base_url = api_key_data['base_url']
        self.client = OpenAI(api_key=api_key, base_url=base_url)


    def chat(self, user_message: str = str):
        LogUtils.info(f"Chat with {self.model}, messages: {user_message}")
        # 当前对话配置
        current_message = {"role": "user", "content": user_message}
        # 历史上下文配置
        self.conversation_history.append(current_message)

        # 判断是否开启上下文，配置 messages
        messages = [{"role": "system", "content": self.prompt}]
        if self.open_history:
            messages.append(*self.conversation_history)
        else:
            messages.append(current_message)

        # 轮询所有 api_key
        while True:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )

                assistant_message = completion.choices[0].message.to_dict()['content']
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                return assistant_message
            except openai.RateLimitError:
                self.setup_client()