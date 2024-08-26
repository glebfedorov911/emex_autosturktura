from fastapi import HTTPException, status

from app.core.models import Proxy, NewFilter, File, Parser
from .schemas import ParserCreate

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select, func, text


async def get_proxies(session: AsyncSession, user_id: int):
    stmt = select(Proxy).where(Proxy.user_id==user_id).where(Proxy._is_banned==False).where(Proxy.is_using==True)
    result: Result = await session.execute(stmt)
    proxies = result.scalars().all()

    # if proxies == []:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Закочнились прокси"
    #     )
    return proxies

async def get_filter(session: AsyncSession, user_id: int, filter_id: int):
    stmt = select(NewFilter).where(NewFilter.user_id == user_id).where(NewFilter.id == filter_id)
    result: Result = await session.execute(stmt)
    filter = result.scalar()

    # if filter is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Неизвестный фильтр"
    #     )

    return filter

async def get_last_upload_files(user_id: int, session: AsyncSession):
    stmt = select(File).where(File.user_id==user_id)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()
    if files == []:
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail="Нет загруженных файлов"
        # )
        return None

    if files[-1].after_parsing_filename != None:
        # raise HTTPException(
        #     status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        #     detail="Данный файл уже спаршен"
        # )
        return None

    return files[-1]

async def saving_to_table_data(user_id: int, session: AsyncSession, data: list):
    for value in data:
        if len(value) == 7:
            parser_in = ParserCreate(article=str(value[0]), number_of_goods=str(value[1]), logo=str(value[2]), delivery=str(value[3]), best_price=str(value[4]), quantity_goods=str(value[5]), price_with_logo=str(value[6]), user_id=user_id)
        else:
            parser_in = ParserCreate(article=str(value[0]), number_of_goods=str(value[1]), logo=str(value[2]), delivery=str(value[3]), best_price=str(value[4]), quantity_goods=str(value[5]), price_with_logo="Цена не найдена", user_id=user_id)
        parser = Parser(**parser_in.model_dump())
        session.add(parser)
        await session.commit()

    return "все успешно сохранено"

async def add_final_file_to_table(user_id: int, session: AsyncSession, result_name: str, filter_id_global: int):
    file = await get_last_upload_files(user_id=user_id, session=session)
    file.after_parsing_filename = result_name
    file.finish_date = datetime.now()
    file.new_filter_id = filter_id_global
    await session.commit()

async def set_banned_proxy(proxy_servers: list, session: AsyncSession):
    for proxy in proxy_servers:
        stmt = select(Proxy).where(Proxy.ip_with_port == proxy.split("@")[0])
        result: Result = await session.execute(stmt)
        proxies = result.scalar()

        proxies._is_banned = True
        proxies.is_using = False
        session.add(proxies)
        await session.commit()

async def unbanned_proxy(session: AsyncSession, user_id: int):
    stmt = select(Proxy).where(Proxy.user_id==user_id).where(Proxy._is_banned==True)
    result: Result = await session.execute(stmt)
    proxies = result.scalars().all()

    for proxy in proxies:
        if (datetime.now() - proxy.when_banned).total_seconds() / 60 >= 1440:
            proxy._is_banned = False
            proxy.is_using = True
            proxy.when_banned = None
            session.add(proxy)
            await session.commit()

async def delete_proxy_banned(session: AsyncSession, user_id: int):
    stmt = select(Proxy).where(Proxy.user_id==user_id).where((Proxy.expired_at - func.now()) < timedelta(days=0))
    result: Result = await session.execute(stmt)
    proxies = result.scalars().all()
    for proxy in proxies:
        proxy.is_using = False
        session.add(proxy)
        await session.commit()