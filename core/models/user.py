from sqlalchemy import String, BigInteger, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from datetime import datetime

from .base import Base


class User(Base):
    username: Mapped[str] = mapped_column(String, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)

    admin: Mapped[bool] = mapped_column(Boolean, default=False)

    premium: Mapped[bool] = mapped_column(Boolean, default=False)
    buy_premium: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    referrer_is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    referrer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    referrer: Mapped["User | None"] = relationship(
        "User", remote_side="User.id", back_populates="referred_users"
    )

    referred_users: Mapped[list["User"]] = relationship(
        "User", remote_side="User.referrer_id", back_populates="referrer"
    )

    request_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    request_reload: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )
