from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from functools import wraps
engine = create_engine(url = "sqlite:///data.db")

session_factory = sessionmaker(engine)


def with_new_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with session_factory() as session:
            return func(session, *args, **kwargs)
    return wrapper



class Base(DeclarativeBase):
    pass

class ChatRequests(Base):
    __tablename__ = "chat_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    ip_adress: Mapped[str] = mapped_column(index=True)
    promt: Mapped[str]
    response: Mapped[str]


@with_new_session
def get_user_requests(session, ip_adress: str, limit: int = 10) -> list[ChatRequests]:
    query = (
        select(ChatRequests)
        .filter_by(ip_adress=ip_adress)
        .order_by(ChatRequests.id.desc())   
        .limit(limit)                       
    )
    result = session.execute(query)
    return list(reversed(result.scalars().all()))

def summarise(ip_adress: str):
    pass

@with_new_session
def add_request_data(session, ip_adress: str, prompt: str, response: str) -> None:

    new_request = ChatRequests(
        ip_adress=ip_adress,
        promt=prompt,
        response=response,
    )
    session.add(new_request)

    session.commit()