from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .proxy import Proxy
    from .filter import Filter
    from .new_filter import NewFilter
    from .file import File
    from .parser import Parser


class User(Base):
    fullname: Mapped[str] = mapped_column(String(256))
    description: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_parsing: Mapped[bool] = mapped_column(default=False, nullable=True)
    proxies: Mapped[list["Proxy"]] = relationship(back_populates="user")
    filters: Mapped[list["Filter"]] = relationship(back_populates="user")
    newfilters: Mapped[list["NewFilter"]] = relationship(back_populates="user")
    files: Mapped[list["File"]] = relationship(back_populates="user")
    parsers: Mapped[list["Parser"]] = relationship(back_populates="user")