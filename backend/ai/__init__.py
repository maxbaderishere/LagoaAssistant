"""Clients for AI models behind a common interface."""

from ai.client import Client
from ai.gemini_client import GeminiClient
from ai.groq_client import GroqClient
from ai.ollama_client import OllamaClient
from ai.registry import ModelInfo, ModelRegistry, UnknownModelError

__all__ = [
    "Client", "GeminiClient", "GroqClient", "OllamaClient",
    "ModelInfo", "ModelRegistry", "UnknownModelError",
]
