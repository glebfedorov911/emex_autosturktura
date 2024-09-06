from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession 
from app.core.models import db_helper
from app.api_v1.auth.utils import get_payload
from . import crud


router = APIRouter(prefix="/nds", tags=["NDS"])

@router.get("/edit/{file_id}")
async def edit_with_nds(file_id: int, payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends)):
    return await crud.edit_with_nds(session=session, user_id=payload.get("sub"), file_id=file_id)