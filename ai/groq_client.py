"""Client for models hosted on Groq."""

from groq import Groq

from ai.client import Client
from db import ChatRequests


class GroqClient(Client):
    """AI client backed by the Groq API."""

    def __init__(self, api_key: str, model: str = "qwen/qwen3.8-27b"):
        """Create a Groq client.

        Args:
            api_key: Groq API key.
            model: Name of the Groq model to use.
        """
        self._client = Groq(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        """Generate an answer with a Groq model.

        The summary, if any, goes first as a system message, followed by the
        history as alternating user and assistant messages.
        """
        messages = []
        if summary:
            messages.append({
                "role": "system",
                "content": f"Краткое содержание вашего прошлого диалога с пользователем:\n{summary}",
            })
        for item in history:
            messages.append({"role": "user", "content": item.promt})
            messages.append({"role": "assistant", "content": item.response})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.completions.create(model=self._model, messages=messages)
        return response.choices[0].message.content or ""