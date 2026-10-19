"""Application settings, loaded from environment variables and the .env file."""

from dotenv import load_dotenv
from pathlib import Path
import os

# The project root, one level above backend/. .env and data.db live there, so
# the app finds them no matter which folder the server is started from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")



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
        database_url: SQLAlchemy URL of the database, ``data.db`` in the project root.
        ollama_url: Address of the local Ollama server, read from ``OLLAMA_URL``.
        models: Models users can pick from. ``provider`` selects the client
            class, ``model`` is the provider's model name and ``name`` is the
            label shown in the interface. A cloud model is only available if
            its provider's API key is set; an Ollama model only if Ollama is
            running and the model is pulled.
        default_model: Model used when the user hasn't picked one.
        title_model: Small model that names new chats, so naming doesn't use
            up the limits of the main models. If it isn't available, the
            chat's own model names it.
        quick_reply_model: Local model that suggests short replies when the
            assistant asks the user something. If it isn't available, no
            suggestions are shown; the cloud models aren't used for this.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    database_url = f"sqlite:///{(PROJECT_ROOT / 'data.db').as_posix()}"
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    jwt_secret = os.getenv("JWT_SECRET")
    jwt_algorithm = "HS256"
    access_token_expire_minutes = 60 * 24 * 7
    models = [
        {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B"},
        {"provider": "gemini", "model": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
        {"provider": "ollama", "model": "qwen3.5:4b", "name": "Qwen 3.5 4B"},
    ]
    default_model = "qwen/qwen3.8-27b"
    title_model = {"provider": "ollama", "model": "qwen3.5:4b"}
    quick_reply_model = {"provider": "ollama", "model": "qwen3.5:4b"}
    keep_last = 10
    summarise_every = 10
cfg = Config()

if not cfg.jwt_secret:
    raise RuntimeError("JWT_SECRET is not set. Add it to .env, see README.")
