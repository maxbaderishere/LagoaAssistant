"""Builds the model registry from the settings in config.py."""

from ai.gemini_client import GeminiClient
from ai.groq_client import GroqClient
from ai.registry import ModelInfo, ModelRegistry
from config import cfg


def build_registry() -> ModelRegistry:
    """Create a client for every model in ``cfg.models`` whose provider has an API key."""
    providers = {
        "groq": (GroqClient, cfg.groq_api_key),
        "gemini": (GeminiClient, cfg.gemini_api_key),
    }
    registry = ModelRegistry()
    for entry in cfg.models:
        client_class, api_key = providers[entry["provider"]]
        if not api_key:
            continue
        registry.register(
            ModelInfo(id=entry["model"], name=entry["name"], provider=entry["provider"]),
            client_class(api_key=api_key, model=entry["model"]),
            default=entry["model"] == cfg.default_model,
        )
    return registry


registry = build_registry()
