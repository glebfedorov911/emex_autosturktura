from fastapi import HTTPException, status

from app.core.models import Proxy, NewFilter, File

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select


async def get_proxies(session: AsyncSession, user_id: int):
    stmt = select(Proxy).where(Proxy.user_id==user_id).where(Proxy._is_banned==False)
    result: Result = await session.execute(stmt)
    proxies = result.scalars().all()
    if proxies == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Закочнились прокси"
        )
    
    return proxies

async def get_filter(session: AsyncSession, user_id: int, filter_id: int):
    stmt = select(NewFilter).where(NewFilter.user_id == user_id).where(NewFilter.id == filter_id)
    result: Result = await session.execute(stmt)
    filter = result.scalar()

    if filter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Неизвестный фильтр"
        )

    return filter

async def get_last_upload_files(user_id: int, session: AsyncSession):
    stmt = select(File).where(File.user_id==user_id)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()
    if files == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет загруженных файлов"
        )

    if files[-1].after_parsing_filename != None:
        raise HTTPException(
            status_code=status.HTTP_405_NOT_FOUND,
            detail="Данный файл уже спаршен"
        )
    
    return files[-1].before_parsing_filename