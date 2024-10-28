from openai import OpenAI
from .RequestUtils import RequestUtils
from .LogUtils import LogUtils

private_api_key = {
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
    def client(cls, api_key: str, base_url: str):
        return cls(api_key, base_url)

    def __chat(self, model: str = "gpt-3.5-turbo", messages: str = "Hello!") -> dict:
        """Chat with GPT"""
        LogUtils.info(f"Chat with {model}, messages: {messages}")
        completion = self.__client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": messages}
            ]
        )
        return completion.choices[0].message.to_dict()

    def chat(self, model: str = "gpt-3.5-turbo", messages: str = "Hello!", prompt: str = "You are a helpful assistant.") -> dict:
        """Chat with GPT"""
        if prompt:
            return self.chat_with_prompt(model, messages, prompt)
        else:
            return self.__chat(model, messages)

    def chat_with_prompt(self, model: str = "gpt-3.5-turbo", messages: str = "Hello!", prompt: str = "You are a helpful assistant."):
        LogUtils.info(f"Chat with {model}, messages: {messages}")
        completion = self.__client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": messages}
            ]
        )
        return completion.choices[0].message.to_dict()