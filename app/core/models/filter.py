from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .file import File


class Filter(Base):
    is_has_logo: Mapped[bool]
    logo: Mapped[str] = mapped_column(String(4))
    is_has_brand: Mapped[bool]
    brand: Mapped[str]
    is_bigger_then_date: Mapped[bool]
    date: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="filters")
    files = relationship("File", back_populates="filters")