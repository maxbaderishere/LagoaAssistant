"""Database models and helpers for storing users, chats and messages.

The schema itself is created and changed by Alembic migrations in ``migrations/``.
"""

from datetime import datetime, timezone

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import DateTime, ForeignKey, MetaData, String, create_engine, delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from functools import wraps

from backend.config import PROJECT_ROOT, cfg

engine = create_engine(url = cfg.database_url)

# expire_on_commit=False keeps loaded attributes available after the session
# closes, so helpers can return model objects to the caller.
session_factory = sessionmaker(engine, expire_on_commit=False)

# Longest chat title; titles made from the first prompt are cut to this length.
TITLE_MAX_LENGTH = 100


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


def _now() -> datetime:
    return datetime.now(timezone.utc)


class LoginTakenError(Exception):
    """Raised when registering a login that already exists."""


class Base(DeclarativeBase):
    """Base class for all ORM models.

    The naming convention gives every constraint a predictable name, so
    migrations can later drop or change it on any database.
    """
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })

class User(Base):
    """A registered user. The password is stored only as a hash."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

class Chat(Base):
    """A conversation of a user. ``title`` is None until the first message names it."""
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str | None] = mapped_column(String(TITLE_MAX_LENGTH))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

class ChatRequests(Base):
    """A single exchange in a chat: the user's prompt and the model's response."""
    __tablename__ = "chat_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), index=True)
    promt: Mapped[str]
    response: Mapped[str]

class ChatSummary(Base):
    """Running summary of a chat's older messages.

    ``last_summarized_id`` is the id of the last message already folded into
    the summary, so only newer messages need to be summarised next time.
    """
    __tablename__ = "chat_summary"
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    text: Mapped[str]
    last_summarized_id: Mapped[int]


def migrate() -> None:
    """Bring the database schema up to date by applying Alembic migrations."""
    alembic_cfg = AlembicConfig(PROJECT_ROOT / "alembic.ini")
    # Keep the server's logging setup; alembic.ini would replace it.
    alembic_cfg.attributes["configure_logger"] = False
    command.upgrade(alembic_cfg, "head")


# ---------- users ----------

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


# ---------- chats ----------

@with_new_session
def create_chat(session, user_id: int, title: str | None = None) -> Chat:
    """Create an empty chat for the user."""
    chat = Chat(user_id=user_id, title=title)
    session.add(chat)
    session.commit()
    return chat


@with_new_session
def get_user_chats(session, user_id: int) -> list[Chat]:
    """Return the user's chats, most recently active first."""
    query = (
        select(Chat)
        .filter_by(user_id=user_id)
        .order_by(Chat.updated_at.desc(), Chat.id.desc())
    )
    return list(session.execute(query).scalars().all())


@with_new_session
def get_user_chat(session, user_id: int, chat_id: int) -> Chat | None:
    """Return the chat if it exists and belongs to the user, otherwise None."""
    return session.execute(
        select(Chat).filter_by(id=chat_id, user_id=user_id)
    ).scalar_one_or_none()


@with_new_session
def rename_chat(session, chat_id: int, title: str) -> Chat:
    """Change a chat's title and return the updated chat."""
    chat = session.get(Chat, chat_id)
    chat.title = title
    session.commit()
    return chat


@with_new_session
def delete_chat(session, chat_id: int) -> None:
    """Delete a chat together with its messages and summary."""
    session.execute(delete(ChatSummary).filter_by(chat_id=chat_id))
    session.execute(delete(ChatRequests).filter_by(chat_id=chat_id))
    session.execute(delete(Chat).filter_by(id=chat_id))
    session.commit()


# ---------- messages ----------

@with_new_session
def get_chat_messages(session, chat_id: int, limit: int | None = None) -> list[ChatRequests]:
    """Return a chat's messages in chronological order.

    Args:
        chat_id: Id of the chat.
        limit: If given, return only this many most recent messages.
    """
    query = (
        select(ChatRequests)
        .filter_by(chat_id=chat_id)
        .order_by(ChatRequests.id.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    result = session.execute(query)
    return list(reversed(result.scalars().all()))


@with_new_session
def add_message(session, chat_id: int, prompt: str, response: str) -> Chat:
    """Save a prompt and the model's response to a chat.

    Marks the chat as recently active, names it after the prompt if it has no
    title yet, and returns the updated chat.
    """
    session.add(ChatRequests(chat_id=chat_id, promt=prompt, response=response))
    chat = session.get(Chat, chat_id)
    chat.updated_at = _now()
    if chat.title is None:
        chat.title = " ".join(prompt.split())[:TITLE_MAX_LENGTH]
    session.commit()
    return chat


# ---------- summaries ----------

@with_new_session
def get_summary(session, chat_id: int) -> ChatSummary | None:
    """Return the chat's conversation summary, or None if there is none yet."""
    return session.get(ChatSummary, chat_id)


@with_new_session
def get_unsummarized_messages(session, chat_id: int, after_id: int) -> list[ChatRequests]:
    """Return the chat's messages with an id greater than ``after_id``, oldest first."""
    query = (
        select(ChatRequests)
        .filter_by(chat_id=chat_id)
        .where(ChatRequests.id > after_id)
        .order_by(ChatRequests.id)
    )
    return list(session.execute(query).scalars().all())


@with_new_session
def save_summary(session, chat_id: int, text: str, last_summarized_id: int) -> None:
    """Create or update the chat's conversation summary."""
    session.merge(ChatSummary(
        chat_id=chat_id,
        text=text,
        last_summarized_id=last_summarized_id,
    ))
    session.commit()
