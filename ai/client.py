"""Abstract base class for AI model clients."""

import re
from abc import ABC, abstractmethod

from db import ChatRequests

# Longest chat title the model is allowed to produce.
TITLE_MAX_LENGTH = 60


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

    def make_title(self, prompt: str, answer: str) -> str:
        """Come up with a short chat title from the first question and answer.

        Args:
            prompt: The first message of the chat.
            answer: The model's reply to it.

        Returns:
            A cleaned-up title, or an empty string if the model gave nothing usable.
        """
        request = (
            "Придумай короткое название для чата по его первому сообщению и ответу. "
            "От 2 до 5 слов, на языке сообщения пользователя, без кавычек, "
            "без точки в конце и без пояснений. Ответь только названием.\n\n"
            f"Сообщение пользователя:\n{prompt[:1000]}\n\n"
            f"Ответ ассистента:\n{answer[:1000]}"
        )
        return clean_title(self.generate(request, history=[]))


def clean_title(raw: str) -> str:
    """Turn a model's reply into a one-line title.

    Drops reasoning blocks like ``<think>...</think>``, markdown, quotes and
    a trailing period, keeps the first non-empty line and caps the length.
    """
    text = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S | re.I)
    line = next((l for l in text.splitlines() if l.strip()), "")
    line = re.sub(r"^(название|title)\s*:\s*", "", line.strip(), flags=re.I)
    wrappers = " \t*#_`\"'«»“”„"
    line = line.strip(wrappers).rstrip(".!").strip(wrappers)
    line = " ".join(line.split())
    if len(line) > TITLE_MAX_LENGTH:
        line = line[:TITLE_MAX_LENGTH].rsplit(" ", 1)[0] + "…"
    return line
