from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    thread_id: Mapped[str] = mapped_column(ForeignKey("threads.id"))
    text: Mapped[str] = mapped_column()
    sender: Mapped[str] = mapped_column(String(10))
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))

    thread: Mapped["Thread"] = relationship(back_populates="messages")


class Thread(Base):
    __tablename__ = "threads"
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(255), default="新規チャット")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))

    messages: Mapped[list["Message"]] = relationship(
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.timestamp",
    )
