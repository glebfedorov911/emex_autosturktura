from fastapi import HTTPException, status

from app.core.models import Proxy, NewFilter, File, Parser, User
from app.api_v1.filters.depends import filter_by_id 
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
    stmt = select(File).where(File.user_id==user_id).order_by(File.id)
    result: Result = await session.execute(stmt)
    files = result.scalars().all()
    if files == []:
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail="Нет загруженных файлов"
        # )
        return None

    if files[-1].is_after_parsing:
        # raise HTTPException(
        #     status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        #     detail="Данный файл уже спаршен"
        # )
        return None
    return files[-1]

def price_without_nds(best_price, price_site):
    if best_price == 0:
        return 0
    price_company = int(float(price_site) * 1.07)
    price_from_site = int(best_price)
    return price_from_site - 1 if price_company < price_from_site else price_company

def price_with_nds(best_price, price_site):
    if best_price == 0:
        return 0
    price_company = int(float(price_site) * 1.27)
    price_from_site = int(best_price)
    return price_from_site - 1 if price_company < price_from_site else price_company

async def saving_to_table_data(user_id: int, session: AsyncSession, data: list, file_id: int):
    for value in data:
        try:
            if len(value) == 14:
                parser_in = ParserCreate(good_code=str(value[0]), article=str(value[1]), name=str(value[2]), brand=str(value[3]), article1=str(value[4]), quantity=str(value[5]), 
                    price=str(value[6]), abcp_price=str(value[7]), batch=str(value[8]),
                    logo=str(value[9]), delivery_time=str(value[10]), best_price=str(value[11]), 
                    best_price_without_nds=str(price_without_nds(value[11], value[6])), best_price_with_nds=str(price_with_nds(value[11], value[6])), 
                    quantity1=str(value[12]), new_price=str(value[13]), user_id=user_id, file_id=file_id)
            else:
                parser_in = ParserCreate(good_code=str(value[0]), article=str(value[1]), name=str(value[2]), brand=str(value[3]), article1=str(value[4]), quantity=str(value[5]), 
                    price=str(value[6]), abcp_price=str(value[7]), batch=str(value[8]),
                    logo=str(value[9]), delivery_time=str(value[10]), best_price=str(value[11]), 
                    best_price_without_nds=str(price_without_nds(value[11], value[6])), best_price_with_nds=str(price_with_nds(value[11], value[6])), 
                    quantity1=str(value[12]), user_id=user_id, file_id=file_id)
            parser = Parser(**parser_in.model_dump())
            session.add(parser)
        except:
            print("choot-to net tak")
            continue
    await session.commit()

    return "все успешно сохранено"

async def get_title_filter(session: AsyncSession, filter_id_global: int):
    stmt = select(NewFilter.title).where(NewFilter.id==filter_id_global)
    result: Result = await session.execute(stmt)
    return result.scalars().all()[0]

async def add_final_file_to_table(user_id: int, session: AsyncSession, filter_id_global: int):
    file = await get_last_upload_files(user_id=user_id, session=session)
    file.is_after_parsing = True
    # file.filename_after_parsing_with_nds = f"ПОСЛЕ_ПАРСИНГА_С_НДС_{file.before_parsing_filename}"
    # file.filename_after_parsing_without_nds = f"ПОСЛЕ_ПАРСИНГА_БЕЗ_НДС_{file.before_parsing_filename}"
    # file.filename_after_parsing = f"ПОСЛЕ_ПАРСИНГА_{file.before_parsing_filename}"
    file.finish_date = datetime.now()
    file.new_filter_id = await get_title_filter(session=session, filter_id_global=filter_id_global)
    await session.commit()

async def set_banned_proxy(proxy_servers: list, session: AsyncSession, user_id: int):
    for proxy in proxy_servers:
        stmt = select(Proxy).where(Proxy.ip_with_port == proxy.split("@")[0]).where(Proxy.user_id==user_id).where(Proxy._is_banned==False)
        result: Result = await session.execute(stmt)
        proxies = result.scalars().all()
        try:
            for pr in proxies:
                pr._is_banned = True
                pr.is_using = False
                pr.when_banned = datetime.now()
                session.add(pr)
        except Exception as e:
            print(e)
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

async def set_parsing(session: AsyncSession, status: bool, user_id: int):
    stmt = select(User).where(User.id==user_id)
    result: Result = await session.execute(stmt)
    user = result.scalar()

    user.is_parsing = status

    session.add(user)
    await session.commit()

async def set_filter_for_parsing_file(session: AsyncSession, filter_id: int, file_id: int) -> None:
    stmt = select(NewFilter).where(NewFilter.id==filter_id)
    result: Result = await session.execute(stmt)
    filter_name = result.scalar().title

    stmt = select(File).where(File.id==file_id)
    result: Result = await session.execute(stmt)
    file = result.scalar()

    file.new_filter_id = filter_name
    session.add(file)
    await session.commit()