from app.api_v1.users.views import router as user_router
from app.api_v1.proxies.views import router as proxy_router
from app.api_v1.filters.views import router as filter_router
from app.api_v1.files.views import router as file_router
from app.api_v1.parser.views import router as parser_router
from app.api_v1.showing.views import router as show_data_router
from app.core.config import settings

from fastapi import APIRouter


router = APIRouter(prefix=settings.api)
router.include_router(user_router)
router.include_router(proxy_router)
router.include_router(filter_router)
router.include_router(file_router)
router.include_router(parser_router)
router.include_router(show_data_router)