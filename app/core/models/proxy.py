from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from datetime import datetime
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Proxy(Base):
    expired_at: Mapped[datetime]
    id_proxy: Mapped[str]
    login: Mapped[str]
    password: Mapped[str]
    ip_with_port: Mapped[str]
    _is_banned: Mapped[bool] = mapped_column(default=False, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="proxies")

    def __str__(self):
        return self.ip_with_port, self.login, self.password, str(self._is_banned), str(self.expired_at)