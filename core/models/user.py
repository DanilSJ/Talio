from sqlalchemy import String, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column
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
