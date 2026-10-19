"""Abstract base class for AI model clients."""

import re
from abc import ABC, abstractmethod

from backend.ai.context import Context
from backend.db import ChatRequests

# Longest chat title the model is allowed to produce.
TITLE_MAX_LENGTH = 60


class Client(ABC):
    """Base class for AI model clients.

    ``generate`` builds the conversation context the same way for every model;
    subclasses only implement ``_complete``, which sends a ready context in
    their provider's format. ``summarise``, ``make_title`` and
    ``suggest_replies`` are built on ``generate`` and work for any model.
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

    def suggest_replies(self, answer: str) -> list[str]:
        """Suggest a few short replies to an answer that ends with a question.

        Args:
            answer: The assistant's latest answer.

        Returns:
            Up to ``MAX_REPLIES`` short replies, or an empty list if the answer
            doesn't ask the user anything.
        """
        ending = answer.strip()[-REPLY_CONTEXT_CHARS:]
        if "?" not in ending:
            return []
        return parse_replies(self.generate(QUICK_REPLY_PROMPT.format(ending=ending), history=[]))


# How many quick replies to show and how much of the answer the model reads.
MAX_REPLIES = 3
REPLY_CONTEXT_CHARS = 600
REPLY_MAX_LENGTH = 40

# The examples matter: without them small models answer as the assistant
# ("Here's how...") instead of suggesting what the user could say.
QUICK_REPLY_PROMPT = """Ты подсказываешь пользователю, что он может ответить ассистенту одним нажатием.
Придумай до 3 коротких ответов ОТ ЛИЦА ПОЛЬЗОВАТЕЛЯ на последний вопрос ассистента: 1-4 слова, на языке ассистента.
Если на вопрос можно ответить «да» или «нет», первые два ответа: «Да» и «Нет» (или «Yes» и «No»).
Пиши каждый ответ с новой строки, без нумерации и пояснений.

Пример. Ассистент: Хотите, я добавлю комментарии к коду?
Да
Нет
Только к сложным местам

Пример. Ассистент: Какой жанр фильмов вам ближе?
Комедии
Фантастика
Детективы

Ассистент: {ending}"""


def parse_replies(raw: str) -> list[str]:
    """Turn a model's reply into a short list of distinct quick replies.

    Accepts one reply per line as well as replies separated by commas or
    semicolons, drops list markers and quotes, and skips replies that are
    too long to fit on a button.
    """
    text = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S | re.I)
    parts = [p for line in text.splitlines() for p in re.split(r"[;,]", line)]
    replies: list[str] = []
    for part in parts:
        reply = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", part)
        reply = " ".join(reply.strip(" \t\"'«»“”„*`").rstrip(".").split())
        if not reply or len(reply) > REPLY_MAX_LENGTH:
            continue
        reply = reply[0].upper() + reply[1:]
        if reply.lower() not in (r.lower() for r in replies):
            replies.append(reply)
        if len(replies) == MAX_REPLIES:
            break
    return replies


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
