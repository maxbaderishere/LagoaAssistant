"""Application settings, loaded from environment variables and the .env file."""

from dotenv import load_dotenv
from pathlib import Path
import os

# The project root, one level above backend/. .env and data.db live there, so
# the app finds them no matter which folder the server is started from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

API_KEY_SUFFIX = "_API_KEY"

# The SQLite database used when DATABASE_URL isn't set.
SQLITE_PATH = PROJECT_ROOT / "data.db"


def load_api_keys() -> dict[str, str]:
    """Collect every ``<NAME>_API_KEY`` environment variable that has a value.

    The dictionary is keyed by the lowercase name: ``GROQ_API_KEY`` becomes
    ``"groq"``. A new key only needs a line in .env, not a change here.
    """
    return {
        name.removesuffix(API_KEY_SUFFIX).lower(): value
        for name, value in os.environ.items()
        if name.endswith(API_KEY_SUFFIX) and value
    }


class Config:
    """Application settings.

    Attributes:
        api_keys: API keys by service, from every ``<NAME>_API_KEY`` variable
            (``groq``, ``gemini``, ``anthropic``...), see ``load_api_keys``.
        jwt_secret: Secret used to sign access tokens, read from ``JWT_SECRET``.
        jwt_algorithm: Algorithm used to sign access tokens.
        access_token_expire_minutes: How long an access token stays valid.
        keep_last: How many recent messages are sent to the model verbatim.
        summarise_every: How many older messages must pile up before the
            conversation summary is updated.
        database_url: SQLAlchemy URL of the database, read from ``DATABASE_URL``,
            e.g. ``postgresql+psycopg://lagoa:secret@localhost:5432/lagoa``.
            Without it the app falls back to SQLite in ``data.db`` in the
            project root, which is fine for trying Lagoa out but not for
            production.
        ollama_url: Address of the local Ollama server, read from ``OLLAMA_URL``.
        chat_models: Models users chat with and pick from in the interface.
            ``provider`` selects the client class, ``model`` is the provider's
            model name and ``name`` is the label shown to users. A cloud model
            is only available if its provider's API key is set; an Ollama
            model only if Ollama is running and the model is pulled.
        default_model: Chat model used when the user hasn't picked one.
        helper_models: Models doing work for the app rather than talking to
            users, by role:

            - ``title``: names new chats;
            - ``quick_replies``: suggests reply buttons under an answer;
            - ``summary``: compresses older messages into the chat's memory.

            A role set to None is done by the chat's own model. Otherwise
            ``fallback`` says what happens if the helper model isn't
            available: ``"chat"`` hands the work to the chat's model, None
            skips it (used for quick replies so they never spend the cloud
            models' limits).
    """
    api_keys = load_api_keys()
    database_url = os.getenv("DATABASE_URL") or f"sqlite:///{SQLITE_PATH.as_posix()}"
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    jwt_secret = os.getenv("JWT_SECRET")
    jwt_algorithm = "HS256"
    access_token_expire_minutes = 60 * 24 * 7
    chat_models = [
        {"provider": "groq", "model": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B"},
        {"provider": "gemini", "model": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
        {"provider": "ollama", "model": "qwen3.5:4b", "name": "Qwen 3.5 4B"},
    ]
    default_model = "qwen/qwen3.8-27b"
    helper_models = {
        "title": {"provider": "ollama", "model": "qwen3.5:4b", "fallback": "chat"},
        "quick_replies": {"provider": "ollama", "model": "qwen3.5:4b", "fallback": None},
        "summary": None,
    }
    keep_last = 10
    summarise_every = 10
cfg = Config()

if not cfg.jwt_secret:
    raise RuntimeError("JWT_SECRET is not set. Add it to .env, see README.")
