from abc import ABC, abstractmethod

from db import ChatRequests


class Client(ABC):
    """Базовый класс для клиентов нейросетей.

    Наследнику достаточно реализовать generate: summarise построен поверх него
    и работает одинаково для любой модели.
    """

    @abstractmethod
    def generate(self, prompt: str, history: list[ChatRequests], summary: str | None = None) -> str:
        """Ответить на prompt с учётом последних сообщений и резюме старого диалога."""

    def summarise(self, old_summary: str, messages: list[ChatRequests]) -> str:
        dialog = "\n".join(f"Пользователь: {m.promt}\nАссистент: {m.response}" for m in messages)
        prompt = (
            "Обнови краткое резюме диалога. Сохрани важные факты о пользователе, "
            "его задачи и договорённости. Пиши кратко, без воды.\n\n"
            f"Текущее резюме:\n{old_summary or 'пока пусто'}\n\n"
            f"Новые сообщения:\n{dialog}"
        )
        return self.generate(prompt, history=[])
