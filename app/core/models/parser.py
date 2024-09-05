from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from datetime import datetime
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .file import File


class Parser(Base):
    article: Mapped[str]
    name: Mapped[str]
    brand: Mapped[str]
    article1: Mapped[str]
    quantity: Mapped[str]
    price: Mapped[str]
    batch: Mapped[str]
    NDS: Mapped[str]
    bestPrice: Mapped[str]
    logo: Mapped[str]
    deliveryTime: Mapped[str]
    newPrice: Mapped[str]
    quantity1: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="parsers")
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=True)
    files = relationship("File", back_populates="parsers")

    # number_of_goods: Mapped[str]
    # logo: Mapped[str]
    # delivery: Mapped[str]
    # best_price: Mapped[str]
    # quantity_goods: Mapped[str]
    # price_with_logo: Mapped[str] = mapped_column(nullable=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    # user = relationship("User", back_populates="parsers")
    # file_id: Mapped[int] = mapped_column(ForeignKey("files.id"), nullable=True)
    # files = relationship("File", back_populates="parsers")