"""Database models and helpers for storing chat history in SQLite."""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from functools import wraps

engine = create_engine(url = "sqlite:///data.db")

session_factory = sessionmaker(engine)


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



class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass

class ChatRequests(Base):
    """A single exchange: the user's prompt and the model's response."""
    __tablename__ = "chat_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    ip_adress: Mapped[str] = mapped_column(index=True)
    promt: Mapped[str]
    response: Mapped[str]

class ChatSummary(Base):
    """Running summary of a user's older messages.

    ``last_summarized_id`` is the id of the last message already folded into
    the summary, so only newer messages need to be summarised next time.
    """
    __tablename__ = "chat_summary"
    ip_adress: Mapped[str] = mapped_column(primary_key=True)
    text: Mapped[str]
    last_summarized_id: Mapped[int]

@with_new_session
def get_summary(session, ip_adress: str) -> ChatSummary | None:
    """Return the user's conversation summary, or None if there is none yet."""
    return session.get(ChatSummary, ip_adress)


@with_new_session
def get_unsummarized_requests(session, ip_adress: str, after_id: int) -> list[ChatRequests]:
    """Return the user's messages with an id greater than ``after_id``, oldest first."""
    query = (
        select(ChatRequests)
        .filter_by(ip_adress=ip_adress)
        .where(ChatRequests.id > after_id)
        .order_by(ChatRequests.id)
    )
    return list(session.execute(query).scalars().all())


@with_new_session
def save_summary(session, ip_adress: str, text: str, last_summarized_id: int) -> None:
    """Create or update the user's conversation summary."""
    session.merge(ChatSummary(
        ip_adress=ip_adress,
        text=text,
        last_summarized_id=last_summarized_id,
    ))
    session.commit()

@with_new_session
def get_user_requests(session, ip_adress: str, limit: int | None = None) -> list[ChatRequests]:
    """Return the user's chat history in chronological order.

    Args:
        ip_adress: IP address that identifies the user.
        limit: If given, return only this many most recent messages.
    """
    query = (
        select(ChatRequests)
        .filter_by(ip_adress=ip_adress)
        .order_by(ChatRequests.id.desc())
    )
    if limit is not None:
        query = query.limit(limit)
    result = session.execute(query)
    return list(reversed(result.scalars().all()))


@with_new_session
def add_request_data(session, ip_adress: str, prompt: str, response: str) -> None:
    """Save a prompt and the model's response to the user's history."""

    new_request = ChatRequests(
        ip_adress=ip_adress,
        promt=prompt,
        response=response,
    )
    session.add(new_request)

    session.commit()
