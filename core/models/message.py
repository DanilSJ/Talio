from sqlalchemy import Text, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Message(Base):
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="messages")
