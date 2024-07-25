from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path


BASE_DIR =  Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

class DBSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = False

class Proxy(BaseModel):
    API_KEY: str = "fea1d0c98a179dfc855b7255d801b7f0"

class Auth(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60*24*30

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: Auth = Auth()
    api: str = "/api/v1"
    proxy: Proxy = Proxy()

settings = Settings()