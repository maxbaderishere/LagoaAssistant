"""Abstract base class for AI model clients."""

from abc import ABC, abstractmethod

from db import ChatRequests


class Client(ABC):
    """Base class for AI model clients.

    Subclasses only need to implement ``generate``: ``summarise`` is built on
    top of it and works the same way for any model.
    """

    @abstractmethod
    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        """Generate an answer to a prompt with conversation context.

        Args:
            prompt: The user's new question.
            history: Recent messages, oldest first, sent to the model verbatim.
            summary: Short summary of older messages, if there is one.

        Returns:
            The model's answer as text.
        """

    def summarise(self, old_summary: str, messages: list[ChatRequests]) -> str:
        """Fold new messages into an existing conversation summary.

        Args:
            old_summary: The current summary, or an empty string if there is none.
            messages: Messages not yet included in the summary, oldest first.

        Returns:
            The updated summary.
        """
        dialog = "\n".join(f"Пользователь: {m.promt}\nАссистент: {m.response}" for m in messages)
        prompt = (
            "Обнови краткое резюме диалога. Сохрани важные факты о пользователе, "
            "его задачи и договорённости. Пиши кратко, без воды.\n\n"
            f"Текущее резюме:\n{old_summary or 'пока пусто'}\n\n"
            f"Новые сообщения:\n{dialog}"
        )
        return self.generate(prompt, history=[])
