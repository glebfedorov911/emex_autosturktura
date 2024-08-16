from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Filter, NewFilter


async def filter_by_id(user_id: int, filter_id: int, session: AsyncSession):
    stmt = select(NewFilter).where(NewFilter.user_id == user_id).where(NewFilter.id == filter_id)
    result: Result = await session.execute(stmt)
    _filter = result.scalar()

    return _filter 

def unknown_filter(_filter):
    if _filter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Неизвестный фильтр | Unknown filter"
        )

async def all_filters(user_id: int, session: AsyncSession):
    stmt = select(NewFilter).where(NewFilter.user_id == user_id)
    result: Result = await session.execute(stmt)
    filters = result.scalars().all()

    return filters