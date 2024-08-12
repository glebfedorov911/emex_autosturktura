import pytest
from httpx import AsyncClient, Cookies

from main import app
from app.core.config import settings
from app.api_v1.parser.schemas import ParserCreate