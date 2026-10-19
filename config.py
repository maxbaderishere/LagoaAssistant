"""Application settings, loaded from environment variables and the .env file."""

from dotenv import load_dotenv
import os
load_dotenv()



class Config:
    """Application settings.

    Attributes:
        gemini_api_key: API key for Google Gemini, read from ``GEMINI_API_KEY``.
        groq_api_key: API key for Groq, read from ``GROQ_API_KEY``.
        jwt_secret: Secret used to sign access tokens, read from ``JWT_SECRET``.
        jwt_algorithm: Algorithm used to sign access tokens.
        access_token_expire_minutes: How long an access token stays valid.
        keep_last: How many recent messages are sent to the model verbatim.
        summarise_every: How many older messages must pile up before the
            conversation summary is updated.
        models: Models users can pick from. ``provider`` selects the client
            class, ``model`` is the provider's model name and ``name`` is the
            label shown in the interface. A model is only available if its
            provider's API key is set.
        default_model: Model used when the user hasn't picked one.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    jwt_secret = os.getenv("JWT_SECRET")
    jwt_algorithm = "HS256"
    access_token_expire_minutes = 60 * 24 * 7
    models = [
        {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B"},
        {"provider": "gemini", "model": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
    ]
    default_model = "qwen/qwen3.8-27b"
    keep_last = 10
    summarise_every = 10
cfg = Config()

if not cfg.jwt_secret:
    raise RuntimeError("JWT_SECRET is not set. Add it to .env, see README.")
