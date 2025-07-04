from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declared_attr,
    DeclarativeBase,
    relationship,
)
from sqlalchemy import String, ForeignKey

from datetime import datetime
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .file import File


class Parser(Base):
    abcp_price: Mapped[str] = mapped_column(nullable=True, default=None)
    good_code: Mapped[str]
    article: Mapped[str]
    name: Mapped[str]
    brand: Mapped[str]
    article1: Mapped[str]
    quantity: Mapped[str]
    price: Mapped[str]
    batch: Mapped[str]
    best_price: Mapped[str]
    best_price_without_nds: Mapped[str]
    best_price_with_nds: Mapped[str]
    logo: Mapped[str]
    delivery_time: Mapped[str]
    new_price: Mapped[str] = mapped_column(nullable=True, default=None)
    quantity1: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="parsers")
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=True)
    files = relationship("File", back_populates="parsers")