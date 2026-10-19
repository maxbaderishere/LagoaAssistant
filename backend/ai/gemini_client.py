"""Client for Google Gemini models."""

from google import genai
from google.genai import types

from backend.ai.client import Client
from backend.db import ChatRequests


class GeminiClient(Client):
    """AI client backed by the Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-3.6-flash"):
        """Create a Gemini client.

        Args:
            api_key: Gemini API key.
            model: Name of the Gemini model to use.
        """
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        """Generate an answer with Gemini.

        The history is sent as alternating user and model turns, and the
        summary, if any, is passed as a system instruction.
        """
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
