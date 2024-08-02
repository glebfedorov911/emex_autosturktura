from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from datetime import datetime
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Parser(Base):
    article: Mapped[str]
    number_of_goods: Mapped[str]
    logo: Mapped[str]
    delivery: Mapped[str]
    best_price: Mapped[str]
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="parsers")