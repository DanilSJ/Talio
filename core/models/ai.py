from sqlalchemy import Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class AI(Base):
    system_prompt: Mapped[str] = mapped_column(Text)
    qwen_use: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
