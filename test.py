import os.path

import openai
import yaml
import itertools
from typing import List, Dict

class ApiKey:
    def __init__(self, config_file: str = os.path.join(os.getcwd(), "file", "api_key.yml")):
        # 加载 API key 和 base_url 的配置
        with open(config_file, 'r') as file:
            self.api_data = yaml.safe_load(file)

        # 构造轮询生成器
        self.api_cycle = itertools.cycle(
            (user, key_data['api_key'], key_data['base_url'])
            for user, keys in self.api_data.items()
            for key_data in keys
        )

    def get_next_api_key(self):
        # 获取下一个 api_key 和 base_url
        user, api_key, base_url = next(self.api_cycle)
        return api_key, base_url


class Prompt:
    CHAT_SYSTEM_CONTENT = "You are a helpful assistant."
    IMAGE_GENERATION_PROMPT = "Create an image based on the following description:"


class OpenAiUtils:
    def __init__(self, api_key_manager: ApiKey, prompt: str = Prompt.CHAT_SYSTEM_CONTENT):
        self.api_key_manager = api_key_manager
        self.prompt = prompt
        self.api_key, self.base_url = self.api_key_manager.get_next_api_key()
        self.conversation_context = []

    def _switch_api_key(self):
        # 切换到下一个 api_key
        self.api_key, self.base_url = self.api_key_manager.get_next_api_key()

    def _call_openai_api(self, messages: List[Dict[str, str]]):
        # 配置 OpenAI 的 API key 和 base_url
        openai.api_key = self.api_key
        openai.api_base = self.base_url

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            return response

        except openai.AuthenticationError:
            # 若 api_key 失效，尝试轮询下一个
            self._switch_api_key()
            return self._call_openai_api(messages)
        except openai.RateLimitError:
            # 若 token 用尽，轮询下一个 api_key
            self._switch_api_key()
            return self._call_openai_api(messages)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def chat(self, user_message: str):
        # 构建聊天消息，使用传入的 Prompt 的 system 指令
        self.conversation_context.append({"role": "user", "content": user_message})

        messages = [{"role": "system", "content": self.prompt}] + self.conversation_context

        response = self._call_openai_api(messages)

        if response:
            ai_response = response['choices'][0]['message']['content']
            self.conversation_context.append({"role": "assistant", "content": ai_response})
            return ai_response
        else:
            return "Error: Failed to get response from OpenAI."

    def generate_image(self, prompt: str):
        openai.api_key = self.api_key
        openai.api_base = self.base_url

        try:
            response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
            return response['data'][0]['url']
        except openai.error.AuthenticationError:
            self._switch_api_key()
            return self.generate_image(prompt)
        except openai.error.RateLimitError:
            self._switch_api_key()
            return self.generate_image(prompt)
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
