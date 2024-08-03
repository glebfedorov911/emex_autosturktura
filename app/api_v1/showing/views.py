from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper
from app.api_v1.users.crud import get_payload
from . import crud


router = APIRouter(prefix="/showing", tags=["Show"])

@router.get("/show_data/")
async def show_data(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.show_data(session=session, user_id=payload.get("sub"), skip=skip, limit=limit)