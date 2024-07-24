from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path


BASE_DIR =  Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

class DBSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = False

class Auth(BaseModel):
    algorithm: str = "RS256"

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: Auth = Auth()
    api: str = "/api/v1"

settings = Settings()