"""Abstract base class for AI model clients."""

from abc import ABC, abstractmethod

from backend.ai.context import Context
from backend.db import ChatRequests


class Client(ABC):
    """Base class for AI model clients: sends a conversation to a model, nothing more.

    ``generate`` builds the conversation context the same way for every model;
    subclasses only implement ``_complete``, which sends a ready context in
    their provider's format. Helper tasks such as naming chats live in
    ``backend.helpers`` and receive a client to work with.
    """

    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        """Generate an answer to a prompt with conversation context.

        Args:
            prompt: The user's new question.
            history: Recent messages, oldest first, sent to the model verbatim.
            summary: Short summary of older messages, if there is one.

        Returns:
            The model's answer as text.
        """
        return self._complete(Context.build(prompt, history, summary))

    @abstractmethod
    def _complete(self, context: Context) -> str:
        """Send the context to the model and return its answer as text."""
