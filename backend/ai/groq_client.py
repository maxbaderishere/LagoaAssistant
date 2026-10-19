"""Client for models hosted on Groq."""

from groq import Groq

from backend.ai.client import Client
from backend.ai.context import Context


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

    def _complete(self, context: Context) -> str:
        """Send the context to a Groq model in the chat format."""
        response = self._client.chat.completions.create(model=self._model, messages=context.as_chat_messages())
        return response.choices[0].message.content or ""
