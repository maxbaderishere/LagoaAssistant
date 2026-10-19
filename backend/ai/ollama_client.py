"""Client for models running locally in Ollama, so Lagoa works without internet."""

import re

import httpx

from backend.ai.client import Client
from backend.db import ChatRequests


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

    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        """Generate an answer with the local model.

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

        response = self._http.post(
            "/api/chat",
            json={"model": self._model, "messages": messages, "stream": False, "think": False},
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
