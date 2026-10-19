"""Summaries of older messages: the chat's long-term memory."""

from backend.ai.client import Client
from backend.db import ChatRequests


class Summariser:
    """Folds new messages into an existing conversation summary."""

    def __init__(self, client: Client):
        self._client = client

    def summarise(self, old_summary: str, messages: list[ChatRequests]) -> str:
        """Return the updated summary.

        Args:
            old_summary: The current summary, or an empty string if there is none.
            messages: Messages not yet included in the summary, oldest first.
        """
        dialog = "\n".join(f"Пользователь: {m.promt}\nАссистент: {m.response}" for m in messages)
        prompt = (
            "Обнови краткое резюме диалога. Сохрани важные факты о пользователе, "
            "его задачи и договорённости. Пиши кратко, без воды.\n\n"
            f"Текущее резюме:\n{old_summary or 'пока пусто'}\n\n"
            f"Новые сообщения:\n{dialog}"
        )
        return self._client.generate(prompt, history=[])
