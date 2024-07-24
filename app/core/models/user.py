from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase
from sqlalchemy import String

from .base import Base


class User(Base):
    fullname: Mapped[str] = mapped_column(String(256))
    description: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    is_admin: Mapped[bool] = mapped_column(default=False)