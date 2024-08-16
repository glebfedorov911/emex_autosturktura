from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select

from app.core.models import Filter, NewFilter
from app.api_v1.filters.schemas import *
from .schemas import FilterCreate, FilterUpdate
from .depends import filter_by_id, unknown_filter, all_filters


async def create_filter(session: AsyncSession, filter_in: FilterCreate, user_id: int):
    filter = NewFilter(**filter_in.model_dump())
    filter.user_id = user_id
    session.add(filter)
    await session.commit()

    return filter

async def get_filter(session: AsyncSession, user_id: int):
    filters = await all_filters(user_id=user_id, session=session)

    return filters

async def get_filter_by_id(session: AsyncSession, user_id: int, filter_id: int):
    _filter = await filter_by_id(session=session, user_id=user_id, filter_id=filter_id)

    unknown_filter(_filter)

    return _filter

async def edit_filter(session: AsyncSession, upd_filter: FilterUpdate, user_id: int, filter_id: int):
    _filter = await filter_by_id(session=session, user_id=user_id, filter_id=filter_id)

    unknown_filter(_filter)

    update_filter = upd_filter.dict(exclude_unset=True)
    for key, value in update_filter.items():
        setattr(_filter, key, value)

    session.add(_filter)
    await session.commit()

    return _filter

async def delete_filter(session: AsyncSession, user_id: int, filter_id: int):
    _filter = await filter_by_id(session=session, user_id=user_id, filter_id=filter_id)

    unknown_filter(_filter)

    await session.delete(_filter)
    await session.commit()

    return await all_filters(user_id=user_id, session=session)