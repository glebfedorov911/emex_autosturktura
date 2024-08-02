from fastapi import HTTPException, status

from app.core.models import Proxy, File
from .depends import get_files, not_files

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select


async def get_proxies(user_id: int, session: AsyncSession):
    stmt = select(Proxy).where(Proxy.user_id == user_id)#.where(Proxy.is_banned==False)
    result: Result = await session.execute(stmt)
    proxies = result.scalars().all()
    
    if proxies == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Прокси закончились"
        )
    return [[proxy.ip_with_port, proxy.login, proxy.password] for proxy in proxies]

async def get_last_upload_files(user_id: int, session: AsyncSession):
    files = await get_files(user_id=user_id, session=session)
    not_files(files)

    return files[-1].before_parsing_filename
        

async def add_after_parsing_file(user_id: int, session: AsyncSession, new_data: dict):
    files = await get_files(user_id=user_id, session=session)
    not_files(files)

    for key, value in new_data.items():
        setattr(files[-1], key, value)

    session.add(files[-1])
    await session.commit()
