from sqlalchemy import Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Channel(Base):
    __tablename__ = "channel"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    channel_id: Mapped[int] = mapped_column(BigInteger)
    welcome_text: Mapped[str] = mapped_column(String)
    welcome_photo: Mapped[str] = mapped_column(String, nullable=True)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    admin: Mapped[bool] = mapped_column(Boolean, default=False)
    channel: Mapped[int] = mapped_column(Integer, ForeignKey("channel.id"), nullable=True)
    banned_bot: Mapped[bool] = mapped_column(Boolean, default=False)


metadata = Base.metadata
