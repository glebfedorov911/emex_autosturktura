from fastapi import HTTPException, status

from app.core.models import Proxy, File

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
    stmt = select(File).where(File.user_id==user_id).order_by(File.date)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()

    files = [_file for _file in files if "дляпарсинг" in _file.before_parsing_filename]

    try:
        return files[-1].before_parsing_filename
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не загружен"
        )