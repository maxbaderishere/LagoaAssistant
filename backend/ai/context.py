"""The conversation context sent to a model, built once for every provider."""

from dataclasses import dataclass
from typing import Literal

from backend.db import ChatRequests

SUMMARY_INSTRUCTION = "Краткое содержание вашего прошлого диалога с пользователем:\n{summary}"


@dataclass(frozen=True)
class Message:
    """One turn of the conversation."""
    role: Literal["user", "assistant"]
    text: str


@dataclass(frozen=True)
class Context:
    """Everything a model needs to answer, in a provider-neutral form.

    Clients only translate it into their API's format: role names and where
    the system text goes differ between providers, the content doesn't.

    Attributes:
        system: Instruction for the model, or None if there is none.
        messages: The conversation, oldest first, ending with the new prompt.
    """
    system: str | None
    messages: list[Message]

    @classmethod
    def build(cls, prompt: str, history: list[ChatRequests], summary: str | None = None) -> "Context":
        """Turn the chat history, the summary of older messages and the new prompt into a context."""
        messages = []
        for item in history:
            messages.append(Message("user", item.promt))
            messages.append(Message("assistant", item.response))
        messages.append(Message("user", prompt))
        system = SUMMARY_INSTRUCTION.format(summary=summary) if summary else None
        return cls(system=system, messages=messages)

    def as_chat_messages(self) -> list[dict]:
        """The context in the common chat format: a system message first, then the turns.

        Used by APIs that follow the OpenAI chat format, such as Groq and Ollama.
        """
        messages = [{"role": "system", "content": self.system}] if self.system else []
        messages += [{"role": m.role, "content": m.text} for m in self.messages]
        return messages
