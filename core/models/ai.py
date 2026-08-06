from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class AI(Base):
    system_prompt: Mapped[str] = mapped_column(Text)
