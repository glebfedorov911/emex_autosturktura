from app.api_v1.users.views import router as user_router
from app.api_v1.proxies.views import router as proxy_router
from app.core.config import settings

from fastapi import APIRouter


router = APIRouter(prefix=settings.api)
router.include_router(user_router)
router.include_router(proxy_router)