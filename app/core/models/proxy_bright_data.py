from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from datetime import datetime
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User


class ProxyBrightData(Base):
    login: Mapped[str] = mapped_column()
    password: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    port: Mapped[str] = mapped_column()

