from fastapi import APIRouter, Depends, Header

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper
from app.api_v1.auth.utils import get_payload

from . import crud


router = APIRouter(prefix="/showing", tags=["Show"])

@router.get("/show_data/{file_id}")
async def show_data(file_id: int, skip: int = 0, limit: int = 10, session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    
    return await crud.show_data(session=session, user_id=payload.get("sub"), skip=skip, limit=limit, file_id=file_id)