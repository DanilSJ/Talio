from typing import List

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
    premium_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    referrer_is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    referrers: Mapped[List["UserReferral"]] = relationship(
        "UserReferral",
        foreign_keys="UserReferral.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    referred_users: Mapped[List["UserReferral"]] = relationship(
        "UserReferral",
        foreign_keys="UserReferral.referrer_id",
        back_populates="referrer",
    )
    request_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    request_reload: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )


class UserReferral(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="referrers"
    )
    referrer: Mapped["User"] = relationship(
        "User", foreign_keys=[referrer_id], back_populates="referred_users"
    )
