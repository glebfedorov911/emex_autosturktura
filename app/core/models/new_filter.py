from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .file import File

class NewFilter(Base):
    deep_filter: Mapped[int] = mapped_column(default=10, nullable=True)
    deep_analog: Mapped[int] = mapped_column(default=10, nullable=True)
    only_first_logo: Mapped[bool] = mapped_column(default=False, nullable=True)
    analog: Mapped[bool] = mapped_column(default=False)
    replacement: Mapped[bool] = mapped_column(default=False, nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    is_bigger: Mapped[bool | None] = mapped_column(default=None, nullable=True)
    date: Mapped[int | None] = mapped_column(default=None, nullable=True)
    logo: Mapped[str | None] = mapped_column(default=None, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    pickup_point: Mapped[int] = mapped_column(default=38760, nullable=True)
    user = relationship("User", back_populates="newfilters")
    # files = relationship("File", back_populates="newfilters")