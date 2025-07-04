from sqlalchemy.orm import Mapped, mapped_column, declared_attr, DeclarativeBase, relationship
from sqlalchemy import String, ForeignKey

from datetime import datetime
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Proxy(Base):
    expired_at: Mapped[datetime]
    id_proxy: Mapped[str] = mapped_column(nullable=True)
    login: Mapped[str]
    password: Mapped[str]
    ip_with_port: Mapped[str]
    _is_banned: Mapped[bool] = mapped_column(default=False, nullable=True)
    when_banned: Mapped[datetime] = mapped_column(nullable=True)
    is_using: Mapped[bool] = mapped_column(default=True, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="proxies")

    def __str__(self):
        return self.ip_with_port, self.login, self.password, str(self._is_banned), str(self.expired_at)
    
    def __repr__(self):
        return f"{self.ip_with_port}, {self.login}, {self.password}, {str(self._is_banned)}, {str(self.expired_at)}"