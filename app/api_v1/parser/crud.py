from fastapi import HTTPException, status

from app.core.models import Proxy, File, Parser
from .depends import get_files, not_files
from .schemas import ParserCreate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select


async def get_proxies(user_id: int, session: AsyncSession):
    stmt = select(Proxy).where(Proxy.user_id == user_id).where(Proxy._is_banned==0)
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

async def add_parser_data(parser_in: ParserCreate, session: AsyncSession):
    parser = Parser(**parser_in.model_dump())
    session.add(parser)
    await session.commit()

    return parser

async def edit_proxy_ban(proxy_server: str, session: AsyncSession):
    stmt = select(Proxy).where(Proxy.ip_with_port == proxy_server[0])
    result: Result = await session.execute(stmt)
    proxies = result.scalar()

    proxies._is_banned = 1
    session.add(proxies)
    await session.commit()