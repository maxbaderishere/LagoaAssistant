"""Clients for AI models behind a common interface."""

from backend.ai.client import Client
from backend.ai.gemini_client import GeminiClient
from backend.ai.groq_client import GroqClient
from backend.ai.ollama_client import OllamaClient
from backend.ai.registry import ModelInfo, ModelRegistry, UnknownModelError

__all__ = [
    "Client", "GeminiClient", "GroqClient", "OllamaClient",
    "ModelInfo", "ModelRegistry", "UnknownModelError",
]
