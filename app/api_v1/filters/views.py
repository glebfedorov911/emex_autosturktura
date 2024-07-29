from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import FilterCreate, FilterUpdate
from app.api_v1.users.crud import get_payload
from app.core.models import db_helper
from app.api_v1.filters import crud


router = APIRouter(prefix="/filters", tags=["Filters"])

@router.post("/create_filter/")
async def create_filter(filter_in: FilterCreate, session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.create_filter(session=session, filter_in=filter_in, user_id=payload.get("sub"))

@router.get("/get_filters/")
async def get_filter(session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.get_filter(session=session, user_id=payload.get("sub"))

@router.get("/get_filter/{filter_id}")
async def get_filter_by_id(filter_id: int, session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.get_filter_by_id(session=session, user_id=payload.get("sub"), filter_id = filter_id)

@router.patch("/edit_filter/{filter_id}")
async def edit_filter(filter_id: int, upd_filter: FilterUpdate, session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.edit_filter(filter_id=filter_id, upd_filter=upd_filter, user_id=payload.get("sub"), session=session)

@router.delete("/delete_filter/{filter_id}")
async def delete_router(filter_id: int, session: AsyncSession = Depends(db_helper.session_depends), payload=Depends(get_payload)):
    return await crud.delete_filter(session=session, user_id=payload.get("sub"), filter_id=filter_id)