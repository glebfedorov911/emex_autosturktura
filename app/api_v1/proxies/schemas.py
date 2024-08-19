from pydantic import BaseModel

from datetime import datetime


class ProxySchemas(BaseModel):
    id_proxy: str
    login: str
    password: str
    ip_with_port: str
    expired_at: datetime
    user_id: int
    _is_banned: bool = False