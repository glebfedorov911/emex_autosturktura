from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

import os


BASE_DIR =  Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

class DBSettings(BaseModel):
    url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    echo: bool = False

class Proxy(BaseModel):
    API_KEY: str = "fea1d0c98a179dfc855b7255d801b7f0"
    URL: str = "https://api.dashboard.proxy.market"

class Auth(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60*24*30

class Templates(BaseModel):
    templates_path: str = "app/templates"

class UploadFiles(BaseModel):
    path_for_upload: Path = BASE_DIR / "upload_file"

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: Auth = Auth()
    api: str = "/api/v1"
    proxy: Proxy = Proxy()
    upload: UploadFiles = UploadFiles()
    templates: Templates = Templates()

settings = Settings()

if not os.path.exists(settings.upload.path_for_upload):
    os.makedirs(settings.upload.path_for_upload)