from google import genai
from google.genai import types

from ai.client import Client
from db import ChatRequests


class GeminiClient(Client):

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        contents = []
        for item in history:
            contents.append({"role": "user", "parts": [{"text": item.promt}]})
            contents.append({"role": "model", "parts": [{"text": item.response}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        config = None
        if summary:
            config = types.GenerateContentConfig(
                system_instruction=f"Краткое содержание вашего прошлого диалога с пользователем:\n{summary}"
            )

        response = self._client.models.generate_content(
            model=self._model, contents=contents, config=config
        )
        return response.text
