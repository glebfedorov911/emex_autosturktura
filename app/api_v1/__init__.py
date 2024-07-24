from api_v1.users.views import router as user_router
from core.config import settings

from fastapi import APIRouter


router = APIRouter(prefix=settings.api)
router.include_router(user_router)