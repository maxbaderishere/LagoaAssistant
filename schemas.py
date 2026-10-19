"""Request and response schemas for the API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuthRequest(BaseModel):
    """Login and password sent to register or sign in."""
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("login", mode="before")
    @classmethod
    def normalize_login(cls, value: str) -> str:
        """Ignore surrounding spaces and letter case, so "Max" and "max " are one account."""
        return value.strip().lower() if isinstance(value, str) else value


class UserOut(BaseModel):
    """Public information about a user. Never includes the password hash."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Access token returned after registration or sign-in."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut
