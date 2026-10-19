"""Client for Google Gemini models."""

from google import genai
from google.genai import types

from backend.ai.client import Client
from backend.ai.context import Context


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

    def _complete(self, context: Context) -> str:
        """Send the context to Gemini.

        Gemini calls the assistant role "model" and takes the system text as
        a system instruction in the config.
        """
        contents = [
            {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.text}]}
            for m in context.messages
        ]
        config = types.GenerateContentConfig(system_instruction=context.system) if context.system else None
        response = self._client.models.generate_content(model=self._model, contents=contents, config=config)
        return response.text
