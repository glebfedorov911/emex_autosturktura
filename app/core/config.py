from pydantic_settings import BaseSettings
from pydantic import BaseModel
from pathlib import Path

import os
from dotenv import load_dotenv


load_dotenv()

BASE_DIR =  Path(__file__).parent.parent

DB_PATH = BASE_DIR / "db.sqlite3"

class DBSettings(BaseModel):
    # url: str = f"sqlite+aiosqlite:///{DB_PATH}"
    url: str = os.getenv("DATABASE_URL")
    echo: bool = False

class Proxy(BaseModel):
    API_KEY: str = os.getenv("API_TOKEN")
    URL: str = "https://proxy6.net/api/"
    path_for_upload: str = BASE_DIR / "forProxy"
    BRIGHT_DATA_TOKEN: str = os.getenv("BRIGHT_DATA_TOKEN")

class Auth(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60*24*30

class Templates(BaseModel):
    templates_path: str = "app/templates"

class UploadFiles(BaseModel):
    path_for_upload: Path = BASE_DIR / "upload_file"

class Docs(BaseModel):
    docs_url: str = ""

class Settings(BaseSettings):
    db: DBSettings = DBSettings()
    auth: Auth = Auth()
    api: str = "/v1"
    proxy: Proxy = Proxy()
    upload: UploadFiles = UploadFiles()
    templates: Templates = Templates()
    docs: Docs = Docs()

settings = Settings()

if not os.path.exists(settings.upload.path_for_upload):
    os.makedirs(settings.upload.path_for_upload)

if not os.path.exists(settings.proxy.path_for_upload):
    os.makedirs(settings.proxy.path_for_upload)