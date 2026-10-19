"""Client for models running locally in Ollama, so Lagoa works without internet."""

import re

import httpx

from backend.ai.client import Client
from backend.ai.context import Context


class OllamaClient(Client):
    """AI client backed by a local Ollama server."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434", timeout: float = 300):
        """Create an Ollama client.

        Args:
            model: Name of a model pulled into Ollama, e.g. from ``ollama pull``.
            base_url: Address of the Ollama server.
            timeout: Seconds to wait for an answer. Local models on a CPU can be slow.
        """
        self._model = model
        self._http = httpx.Client(base_url=base_url, timeout=timeout)

    def _complete(self, context: Context) -> str:
        """Send the context to the local model in the chat format."""
        response = self._http.post(
            "/api/chat",
            json={"model": self._model, "messages": context.as_chat_messages(), "stream": False, "think": False},
        )
        response.raise_for_status()
        text = response.json()["message"]["content"]
        # Some models still put their reasoning inline; the user only needs the answer.
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def list_local_models(base_url: str = "http://localhost:11434") -> set[str] | None:
    """Return the names of models pulled into Ollama, or None if Ollama isn't running."""
    try:
        response = httpx.get(f"{base_url}/api/tags", timeout=2)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return {m["name"] for m in response.json().get("models", [])}
