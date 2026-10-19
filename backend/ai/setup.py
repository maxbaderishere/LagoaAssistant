"""Builds the model registry and the helper clients from the settings in config.py."""

import logging

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
    if provider == "gemini":
        return GeminiClient(api_key=cfg.gemini_api_key, model=model) if cfg.gemini_api_key else None
    if provider == "ollama":
        return OllamaClient(model=model, base_url=cfg.ollama_url) if _ollama_has(model) else None
    raise ValueError(f"Unknown provider: {provider}")


def build_registry() -> ModelRegistry:
    """Register every model from ``cfg.models`` that can be used right now."""
    registry = ModelRegistry()
    for entry in cfg.models:
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


registry = build_registry()
title_client: Client | None = make_client(cfg.title_model) if cfg.title_model else None
quick_reply_client: Client | None = make_client(cfg.quick_reply_model) if cfg.quick_reply_model else None
