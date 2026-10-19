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
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    jwt_secret = os.getenv("JWT_SECRET")
    jwt_algorithm = "HS256"
    access_token_expire_minutes = 60 * 24 * 7
    keep_last = 10
    summarise_every = 10
cfg = Config()

if not cfg.jwt_secret:
    raise RuntimeError("JWT_SECRET is not set. Add it to .env, see README.")
