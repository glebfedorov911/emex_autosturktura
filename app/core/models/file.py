from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from typing import TYPE_CHECKING
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .filter import Filter
    from .new_filter import NewFilter


class File(Base):
    before_parsing_filename: Mapped[str]
    after_parsing_filename: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(default=datetime.now)
    finish_date: Mapped[datetime] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="files")
    filter_id: Mapped[list[int]] = mapped_column(ForeignKey("filters.id"), nullable=True)
    filters = relationship("Filter", back_populates="files")
    new_filter_id: Mapped[list[int]] = mapped_column(ForeignKey("newfilters.id"), nullable=True)
    newfilters = relationship("NewFilter", back_populates="files")