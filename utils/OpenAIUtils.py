import json
from openai import OpenAI
from .RequestUtils import RequestUtils
from .LogUtils import LogUtils

class ApiKey:
    __api_key: dict[str, list] = {
        'jyz': [
            {
                "api_key": "sk-038BMFFUtSx7mSsVaWr5PQHkh0EnYOkfElZB3X1vECYiASNF",
                "base_url": "https://api.chatanywhere.tech/v1"
            }
        ],
        'mh': [
            {
                "api_key": "sk-jZsOhotwvcWSjmYklOyNuxsBd4incHIdrdpqVDzJHl1JQkNr",
                "base_url": "https://api.chatanywhere.tech/v1"
            }
        ]
    }
    API_2233: str = "sk-PqKd88dce401bc243411d33ae8a8d7a0b85c2ee78b674Ks1"

    @classmethod
    def get_api_key(cls,usr: str = 'mh') -> dict:
        if len(cls.__api_key[usr]) > 0:
            return cls.__api_key[usr][0]

    @classmethod
    def delete_api_key(cls, usr: str = 'mh', idx: int = 0):
        if len(cls.__api_key[usr]) > 0:
            del cls.__api_key[usr][idx]

class Prompt:
    SEO = r"""#01 You are a professional article SEO optimization master.
#02 Your task is to extract a description of about 150 words and 5-7 keywords from the article I provide. 
#03 Follow the user’s requirements carefully & to the letter.
#04 You must respond to my request in the following format, structured as follows: description: #{1}#{2}keyword: #{3}.Among them, #{1} is filled with a description, #{2} is filled with two line breaks, and #{3} is filled with a keyword.
#05 Ensure that the description and keywords are primarily in Chinese.
#06 Your description and keywords for the summary must be completely dependent on the article provided by the user.
#07 If the article provided by the user has too few words, the #02 may not be followed.
#08 Your responses should be informative and logical.
#09 You can only give one reply for each conversation turn.
"""


class OpenAIUtils:
    __api_key: str = None
    __model: str = 'gpt-3.5-turbo'
    __base_url: str = None
    __client: OpenAI = None

    def __init__(self, api_key: str, base_url: str):
        self.__api_key = api_key
        self.__base_url = base_url
        self.__client = OpenAI(api_key=api_key, base_url=base_url)

    @classmethod
    def client(cls, api_key: str = None, base_url: str = None):
        if not api_key:
            api_key = ApiKey.get_api_key('mh')['api_key']
            base_url = ApiKey.get_api_key('mh')['base_url']
        return cls(api_key, base_url)

    def __chat(self, model: str = "gpt-3.5-turbo", message: str = "Hello!") -> dict:
        """Chat with GPT"""
        LogUtils.info(f"Chat with {model}, messages: {message}")
        completion = self.__client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.to_dict()

    def chat(self, model: str = "gpt-3.5-turbo", message: str = "Hello!", prompt: str = "You are a helpful assistant.") -> dict:
        """Chat with GPT"""
        if prompt:
            return self.chat_with_prompt(model, message, prompt)
        else:
            return self.__chat(model, message)

    def chat_with_prompt(self, model: str = "gpt-3.5-turbo", message: str = "Hello!", prompt: str = "You are a helpful assistant."):
        LogUtils.info(f"Chat with {model}, messages: {message}")
        completion = self.__client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.to_dict()

    @staticmethod
    def chat_with_2233ai_with_prompt(model: str = "gpt-4o-mini",
                                     api_key: str = "sk-PqKd88dce401bc243411d33ae8a8d7a0b85c2ee78b674Ks1",
                                     message: str = "Hello!",
                                     prompt: str = Prompt.SEO,
                                     open_proxy: bool = True,
                                     use_local: bool = False) -> dict:
        base_url = "https://api.gptsapi.net/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "type": "json", "content": message}
            ]
        }
        response = RequestUtils.post(base_url, headers=headers, json=payload, open_proxy=open_proxy, use_local=use_local)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")