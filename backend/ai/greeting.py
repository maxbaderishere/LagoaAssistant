"""Welcome screen texts written by a model: a greeting, a subtitle and input hints."""

import random
import re
from dataclasses import dataclass, field

from backend.ai.client import Client

LANGUAGE_NAMES = {"ru": "Russian", "en": "English", "pt": "Brazilian Portuguese", "es": "Spanish"}
PERIOD_NAMES = {
    "morning": "morning (5:00-12:00)",
    "day": "afternoon (12:00-18:00)",
    "evening": "evening (18:00-23:00)",
    "night": "night (23:00-5:00), the user is up late",
}

HINT_COUNT = 4
TITLE_MAX_LENGTH = 40
SUBTITLE_MAX_LENGTH = 70
HINT_MAX_LENGTH = 50

# Hints are about topics picked at random for every request: given an example
# list instead, small models just translate it and every screen looks the same.
HINT_TOPICS = [
    "cooking", "travel", "programming", "studying", "fitness", "personal finance",
    "writing an email", "books", "films", "science", "history", "gardening",
    "learning a language", "music", "productivity", "a gift idea", "home repair",
    "psychology", "space", "a job interview",
]

PROMPT = """You write the welcome screen of a calm and friendly personal AI assistant.
The assistant greets the user. Language: {language}. Time of day for the user: {period}.{topic}

Rules:
- The greeting must match the time of day: never wish a good morning in the evening or a good day at night.
- Don't use the assistant's name and don't address the assistant.
- HINT lines are requests the USER could type to the assistant, in the imperative ("Help me...", "Explain..."), not questions to the user.
- Write the hints about these topics, one each: {hint_topics}.
- Write in natural, grammatical {language}. Keep the English labels TITLE, SUBTITLE, HINT.

Format:
TITLE: a warm, original greeting of 2-5 words
SUBTITLE: one short inviting question, up to 8 words
HINT: a request, up to 6 words
HINT: a request, up to 6 words
HINT: a request, up to 6 words
HINT: a request, up to 6 words

Only these lines, no explanations, no quotes, no emoji."""

TOPIC_LINE = "\nThe user's last conversation was about: {title}. The subtitle may refer to it, but doesn't have to."


@dataclass
class Greeting:
    """Texts for the welcome screen. Empty fields mean the model gave nothing usable."""
    title: str = ""
    subtitle: str = ""
    hints: list[str] = field(default_factory=list)


def make_greeting(client: Client, lang: str, period: str, last_topic: str | None = None) -> Greeting:
    """Ask a model for welcome screen texts.

    Args:
        client: The model that writes the texts, normally the small helper model.
        lang: Interface language code: ru, en, pt or es.
        period: Time of day for the user: morning, day, evening or night.
        last_topic: Title of the user's latest chat, used as an optional hint.
    """
    language = LANGUAGE_NAMES[lang]
    prompt = PROMPT.format(
        language=language,
        period=PERIOD_NAMES[period],
        topic=TOPIC_LINE.format(title=last_topic) if last_topic else "",
        hint_topics=", ".join(random.sample(HINT_TOPICS, HINT_COUNT)),
    )
    return parse_greeting(client.generate(prompt, history=[]))


def _clean(text: str, limit: int) -> str:
    text = " ".join(text.strip(" \t*#_`\"'«»“”„").split())
    return text if 0 < len(text) <= limit else ""


def parse_greeting(raw: str) -> Greeting:
    """Read the TITLE / SUBTITLE / HINT lines from a model's reply, skipping anything malformed.

    Small models sometimes drop or translate the labels; then the lines are
    taken in order: title, subtitle, then hints.
    """
    text = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S | re.I)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    labelled = [re.match(r"^\W*(TITLE|SUBTITLE|HINT)\W*:\s*(.+)$", line, flags=re.I) for line in lines]
    if any(labelled):
        pairs = [(m.group(1).upper(), m.group(2)) for m in labelled if m]
    else:
        keys = ["TITLE", "SUBTITLE"] + ["HINT"] * HINT_COUNT
        pairs = list(zip(keys, (re.sub(r"^[^:]{0,25}:\s*", "", line) for line in lines)))
    greeting = Greeting()
    for key, value in pairs:
        if key == "TITLE" and not greeting.title:
            title = _clean(value, TITLE_MAX_LENGTH).rstrip(".")
            # Shouting ("ПОДРОБНЕЕ") or naming the assistant itself reads as a glitch.
            if not title.isupper() and "lagoa" not in title.lower():
                greeting.title = title
        elif key == "SUBTITLE" and not greeting.subtitle:
            greeting.subtitle = _clean(value, SUBTITLE_MAX_LENGTH)
        elif key == "HINT" and len(greeting.hints) < HINT_COUNT:
            hint = _clean(value, HINT_MAX_LENGTH).rstrip(".")
            if hint.isupper():
                hint = hint.capitalize()
            if hint and hint.lower() not in (h.lower() for h in greeting.hints):
                greeting.hints.append(hint)
    return greeting
