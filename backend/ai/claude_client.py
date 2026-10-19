"""Client for Anthropic's Claude models."""

import anthropic

from backend.ai.client import Client
from backend.ai.context import Context


class ClaudeRefusalError(Exception):
    """Raised when Claude (and its fallback model) declined to answer."""


class ClaudeClient(Client):
    """AI client backed by the Anthropic API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-opus-5-5",
        effort: str = "medium",
        max_tokens: int = 16000,
    ):
        """Create a Claude client.

        Args:
            api_key: Anthropic API key.
            model: Claude model ID, e.g. ``claude-opus-5-5``.
            effort: How much the model thinks before answering: ``low``,
                ``medium``, ``high``, ``xhigh`` or ``max``. Higher is better
                for hard tasks but slower and more expensive.
            max_tokens: Upper limit on the length of an answer.
        """
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._effort = effort
        self._max_tokens = max_tokens

    def _complete(self, context: Context) -> str:
        """Send the context to Claude; the system text goes into the ``system`` parameter.

        Raises:
            ClaudeRefusalError: If the request was declined for safety reasons.
        """
        request = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "messages": [{"role": m.role, "content": m.text} for m in context.messages],
            "output_config": {"effort": self._effort},
            # If Claude declines a request on safety grounds, the API retries it
            # on a fallback model chosen by the refusal category.
            "betas": ["server-side-fallback-2026-07-01"],
            "fallbacks": "default",
        }
        if context.system:
            request["system"] = context.system

        response = self._client.beta.messages.create(**request)
        if response.stop_reason == "refusal":
            raise ClaudeRefusalError(response.stop_details.explanation if response.stop_details else "")
        return "".join(block.text for block in response.content if block.type == "text")
