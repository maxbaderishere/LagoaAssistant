"""Endpoint with the welcome screen texts written by the helper model."""

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, status

from backend.ai.greeting import make_greeting
from backend.ai.setup import title_client
from backend.auth import CurrentUser
from backend.db import get_user_chats
from backend.schemas import GreetingResponse

router = APIRouter(tags=["welcome"])
logger = logging.getLogger(__name__)


@router.get("/greeting")
def greeting(
    user: CurrentUser,
    lang: Literal["ru", "en", "pt", "es"] = "ru",
    period: Literal["morning", "day", "evening", "night"] = "day",
) -> GreetingResponse:
    """Return a greeting, a subtitle and input hints for the welcome screen.

    The texts are written by the helper model in the given language and for
    the user's time of day; the title of the user's latest chat is offered to
    the model as an optional topic. The browser caches the result, so this is
    called about once per part of the day.

    Raises:
        HTTPException: 503 if the helper model isn't available or failed;
            the interface then keeps its built-in texts.
    """
    if title_client is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No helper model")
    chats = get_user_chats(user_id=user.id)
    last_topic = chats[0].title if chats else None
    try:
        result = make_greeting(title_client, lang, period, last_topic)
    except Exception:
        logger.exception("Couldn't generate a greeting")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Helper model failed")
    if not result.title:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Helper model gave no greeting")
    return GreetingResponse(title=result.title, subtitle=result.subtitle, hints=result.hints)
