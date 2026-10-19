"""Database models and helpers for storing users and chat history in SQLite."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from functools import wraps

engine = create_engine(url = "sqlite:///data.db")

# expire_on_commit=False keeps loaded attributes available after the session
# closes, so helpers can return model objects to the caller.
session_factory = sessionmaker(engine, expire_on_commit=False)


def with_new_session(func):
    """Run the decorated function inside a fresh database session.

    The session is opened before the call, passed to the function as its first
    argument and closed afterwards, so callers don't pass it themselves.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with session_factory() as session:
            return func(session, *args, **kwargs)
    return wrapper


class LoginTakenError(Exception):
    """Raised when registering a login that already exists."""


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass

class User(Base):
    """A registered user. The password is stored only as a hash."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class ChatRequests(Base):
    """A single exchange: the user's prompt and the model's response."""
    __tablename__ = "chat_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    promt: Mapped[str]
    response: Mapped[str]

class ChatSummary(Base):
    """Running summary of a user's older messages.

    ``last_summarized_id`` is the id of the last message already folded into
    the summary, so only newer messages need to be summarised next time.
    """
    __tablename__ = "chat_summary"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    text: Mapped[str]
    last_summarized_id: Mapped[int]


@with_new_session
def create_user(session, login: str, password_hash: str) -> User:
    """Create a user.

    Raises:
        LoginTakenError: If a user with this login already exists.
    """
    user = User(login=login, password_hash=password_hash)
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise LoginTakenError(login)
    session.refresh(user)
    return user


@with_new_session
def get_user(session, user_id: int) -> User | None:
    """Return the user with this id, or None if there is none."""
    return session.get(User, user_id)


@with_new_session
def get_user_by_login(session, login: str) -> User | None:
    """Return the user with this login, or None if there is none."""
    return session.execute(select(User).filter_by(login=login)).scalar_one_or_none()


@with_new_session
def get_summary(session, user_id: int) -> ChatSummary | None:
    """Return the user's conversation summary, or None if there is none yet."""
    return session.get(ChatSummary, user_id)


@with_new_session
def get_unsummarized_requests(session, user_id: int, after_id: int) -> list[ChatRequests]:
    """Return the user's messages with an id greater than ``after_id``, oldest first."""
    query = (
        select(ChatRequests)
        .filter_by(user_id=user_id)
        .where(ChatRequests.id > after_id)
        .order_by(ChatRequests.id)
    )
    return list(session.execute(query).scalars().all())


@with_new_session
def save_summary(session, user_id: int, text: str, last_summarized_id: int) -> None:
    """Create or update the user's conversation summary."""
    session.merge(ChatSummary(
        user_id=user_id,
        text=text,
        last_summarized_id=last_summarized_id,
    ))
    session.commit()

@with_new_session
def get_user_requests(session, user_id: int, limit: int | None = None) -> list[ChatRequests]:
    """Return the user's chat history in chronological order.

    Args:
        user_id: Id of the user whose history to return.
        limit: If given, return only this many most recent messages.
    """
    query = (
        select(ChatRequests)
        .filter_by(user_id=user_id)
        .order_by(ChatRequests.id.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    result = session.execute(query)
    return list(reversed(result.scalars().all()))


@with_new_session
def add_request_data(session, user_id: int, prompt: str, response: str) -> None:
    """Save a prompt and the model's response to the user's history."""

    new_request = ChatRequests(
        user_id=user_id,
        promt=prompt,
        response=response,
    )
    session.add(new_request)

    session.commit()
