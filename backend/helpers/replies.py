"""Quick replies: buttons with short answers to the assistant's question."""

import re

from backend.ai.client import Client

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


class ReplySuggester:
    """Suggests a few short replies to an answer that ends with a question."""

    def __init__(self, client: Client):
        self._client = client

    def suggest(self, answer: str) -> list[str]:
        """Return up to ``MAX_REPLIES`` short replies, or none if the answer asks nothing.

        Args:
            answer: The assistant's latest answer.
        """
        ending = answer.strip()[-REPLY_CONTEXT_CHARS:]
        if "?" not in ending:
            return []
        return parse_replies(self._client.generate(QUICK_REPLY_PROMPT.format(ending=ending), history=[]))


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
