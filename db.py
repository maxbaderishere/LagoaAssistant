from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

engine = create_engine(url = "sqlite:///data.db")

session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class ChatRequests(Base):
    __tablename__ = "chat_request"
    id: Mapped[int] = mapped_column(primary_key=True)
    ip_adress: Mapped[str] = mapped_column(index=True)
    promt: Mapped[str]
    response: Mapped[str]


def get_user_requests(ip_adress: str) -> list[ChatRequests]:
    with session() as new_session:
        query = select(ChatRequests).filter_by(ip_adress=ip_adress)
        result = new_session.execute(query)
        return result.scalars().all()


def add_request_data(ip_adress: str, prompt: str, response: str) -> None:
    with session() as new_session:
        new_request = ChatRequests(
            ip_adress=ip_adress,
            promt=prompt,
            response=response,
        )
        new_session.add(new_request)

        new_session.commit()