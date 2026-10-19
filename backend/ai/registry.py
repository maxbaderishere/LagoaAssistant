"""Registry of the AI models the app can use, keyed by model id."""

from dataclasses import dataclass

from backend.ai.client import Client


class UnknownModelError(Exception):
    """Raised when a model id is not in the registry."""


@dataclass(frozen=True)
class ModelInfo:
    """Public description of a model, shown to users when they pick one."""
    id: str
    name: str
    provider: str


class ModelRegistry:
    """Keeps a client for every available model and returns the one asked for.

    Every client implements the same ``Client`` interface, so callers don't
    need to know which provider is behind a model id.
    """

    def __init__(self) -> None:
        self._clients: dict[str, Client] = {}
        self._models: dict[str, ModelInfo] = {}
        self._default_id: str | None = None

    def register(self, info: ModelInfo, client: Client, default: bool = False) -> None:
        """Add a model. The first registered model is the default unless another is marked."""
        self._clients[info.id] = client
        self._models[info.id] = info
        if default or self._default_id is None:
            self._default_id = info.id

    def get(self, model_id: str | None = None) -> Client:
        """Return the client for a model id, or the default client if no id is given.

        Raises:
            UnknownModelError: If the id is not registered.
        """
        model_id = model_id or self.default_id
        if model_id not in self._clients:
            raise UnknownModelError(model_id)
        return self._clients[model_id]

    @property
    def default_id(self) -> str:
        """Id of the model used when the user hasn't picked one."""
        if self._default_id is None:
            raise UnknownModelError("No models are registered")
        return self._default_id

    def models(self) -> list[ModelInfo]:
        """Return all registered models in registration order."""
        return list(self._models.values())
