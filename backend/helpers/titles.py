"""Naming new chats."""

import re

from backend.ai.client import Client

# Longest chat title the model is allowed to produce.
TITLE_MAX_LENGTH = 60


class TitleWriter:
    """Comes up with a short chat title from the chat's first question and answer."""

    def __init__(self, client: Client):
        self._client = client

    def write(self, prompt: str, answer: str) -> str:
        """Return a cleaned-up title, or an empty string if the model gave nothing usable.

        Args:
            prompt: The first message of the chat.
            answer: The model's reply to it.
        """
        request = (
            "Придумай короткое название для чата по его первому сообщению и ответу. "
            "От 2 до 5 слов, на языке сообщения пользователя, без кавычек, "
            "без точки в конце и без пояснений. Ответь только названием.\n\n"
            f"Сообщение пользователя:\n{prompt[:1000]}\n\n"
            f"Ответ ассистента:\n{answer[:1000]}"
        )
        return clean_title(self._client.generate(request, history=[]))


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
