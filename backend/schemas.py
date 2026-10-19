"""Request and response schemas for the API."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator


def _as_utc(value: datetime) -> datetime:
    # SQLite drops the time zone, so times come back naive although they're
    # stored in UTC. Marking them as UTC makes the JSON end with "+00:00",
    # and the browser converts them to the user's local time correctly.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


UtcDatetime = Annotated[datetime, AfterValidator(_as_utc)]


class AuthRequest(BaseModel):
    """Login and password sent to register or sign in."""
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("login", mode="before")
    @classmethod
    def normalize_login(cls, value: str) -> str:
        """Ignore surrounding spaces and letter case, so "Max" and "max " are one account."""
        return value.strip().lower() if isinstance(value, str) else value


class PromptRequest(BaseModel):
    """A question for the assistant and, optionally, the model to answer it."""
    prompt: str = Field(min_length=1)
    model: str | None = None


class ModelOut(BaseModel):
    """A model the user can pick."""
    id: str
    name: str
    provider: str


class ModelsResponse(BaseModel):
    """Available models and the one used by default."""
    default: str
    models: list[ModelOut]


class ChatOut(BaseModel):
    """A chat in the user's list. ``title`` is None until the first message names it."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str | None
    created_at: UtcDatetime
    updated_at: UtcDatetime


class ChatRename(BaseModel):
    """New title for a chat."""
    title: str = Field(min_length=1, max_length=100)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: str) -> str:
        """Collapse whitespace so a title of only spaces counts as empty."""
        return " ".join(value.split()) if isinstance(value, str) else value


class MessageOut(BaseModel):
    """One exchange in a chat."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    promt: str
    response: str


class AnswerResponse(BaseModel):
    """The model's reply, which model wrote it, and the updated chat."""
    answer: str
    model: str
    chat: ChatOut


class SuggestionsResponse(BaseModel):
    """Short replies the user can send with one click; empty if there are none."""
    suggestions: list[str]


class GreetingResponse(BaseModel):
    """Welcome screen texts written by the helper model."""
    title: str
    subtitle: str
    hints: list[str]


class UserOut(BaseModel):
    """Public information about a user. Never includes the password hash."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    created_at: UtcDatetime


class TokenResponse(BaseModel):
    """Access token returned after registration or sign-in."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
