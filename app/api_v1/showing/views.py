from fastapi import APIRouter, Depends, Header

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import db_helper
from app.api_v1.users.crud import get_payload
from app.api_v1.auth.depends import check_payload
from . import crud


router = APIRouter(prefix="/showing", tags=["Show"])

@router.get("/show_data")
async def show_data(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(db_helper.session_depends), access_token: str | None = Header(default=None, convert_underscores=False)):
    payload = await check_payload(access_token=access_token)
    return await crud.show_data(session=session, user_id=payload.get("sub"), skip=skip, limit=limit)