"""Builds the chat model registry and the helper model clients from the settings in config.py."""

import logging

from backend.ai.claude_client import ClaudeClient
from backend.ai.client import Client
from backend.ai.gemini_client import GeminiClient
from backend.ai.groq_client import GroqClient
from backend.ai.ollama_client import OllamaClient, list_local_models
from backend.ai.registry import ModelInfo, ModelRegistry
from backend.config import cfg

logger = logging.getLogger(__name__)

# Models pulled into Ollama; None if Ollama isn't running. Checked once at startup.
_local_models: set[str] | None = list_local_models(cfg.ollama_url)


def _ollama_has(model: str) -> bool:
    if _local_models is None:
        return False
    # "llama3.2" in the settings matches "llama3.2:latest" in Ollama.
    return model in _local_models or f"{model}:latest" in _local_models


def make_client(entry: dict) -> Client | None:
    """Create a client for a model entry from config.py, or None if it can't be used now."""
    provider, model = entry["provider"], entry["model"]
    if provider == "groq":
        return GroqClient(api_key=cfg.groq_api_key, model=model) if cfg.groq_api_key else None
    if provider == "claude":
        return ClaudeClient(api_key=cfg.anthropic_api_key, model=model) if cfg.anthropic_api_key else None
    if provider == "gemini":
        return GeminiClient(api_key=cfg.gemini_api_key, model=model) if cfg.gemini_api_key else None
    if provider == "ollama":
        return OllamaClient(model=model, base_url=cfg.ollama_url) if _ollama_has(model) else None
    raise ValueError(f"Unknown provider: {provider}")


def build_registry() -> ModelRegistry:
    """Register every chat model from ``cfg.chat_models`` that can be used right now."""
    registry = ModelRegistry()
    for entry in cfg.chat_models:
        client = make_client(entry)
        if client is None:
            logger.warning("Model %s (%s) is not available", entry["model"], entry["provider"])
            continue
        registry.register(
            ModelInfo(id=entry["model"], name=entry["name"], provider=entry["provider"]),
            client,
            default=entry["model"] == cfg.default_model,
        )
    return registry


def build_helper_clients() -> dict[str, Client]:
    """Create a client for every helper role in ``cfg.helper_models`` whose model is available."""
    clients = {}
    for role, entry in cfg.helper_models.items():
        if entry is None:
            continue
        client = make_client(entry)
        if client is None:
            logger.warning("Helper model %s (%s) for %r is not available", entry["model"], entry["provider"], role)
            continue
        clients[role] = client
    return clients


registry = build_registry()
_helper_clients = build_helper_clients()


def helper_client(role: str, chat_client: Client) -> Client | None:
    """Return the client that does a helper role for a chat, or None if nobody should.

    Args:
        role: A key of ``cfg.helper_models``, e.g. ``"title"``.
        chat_client: The client of the chat's own model.

    Returns:
        The role's helper model if it's available; otherwise the chat's model
        if the role has no helper model or falls back to the chat, or None if
        the role is skipped when its helper model is missing.

    Raises:
        KeyError: If the role isn't in ``cfg.helper_models``, e.g. a typo.
    """
    entry = cfg.helper_models[role]
    if entry is None:
        return chat_client
    if role in _helper_clients:
        return _helper_clients[role]
    return chat_client if entry.get("fallback") == "chat" else None
