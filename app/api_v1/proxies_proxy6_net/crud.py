from fastapi import UploadFile, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.sql import func

from app.core.config import settings
from app.core.models import Proxy
from .depends import *
from .schemas import ProxySchemas

import os
import pandas as pd
import requests
import json
import datetime


# D:\_.programming\emex_autosturktura\ProxyShablon.xlsx

# data = pd.read_excel("D:\_.programming\emex_autosturktura\ProxyShablon.xlsx").values.tolist()
# print(data)

async def get_proxies(session: AsyncSession, user_id: int, date: str | datetime.datetime | None = None):
    if date:
        stmt = select(Proxy).where(Proxy.expired_at == date).where(Proxy.user_id == user_id)
    else:
        stmt = select(Proxy).where(Proxy.user_id == user_id)
    results: Result = await session.execute(stmt)
    proxies = results.scalars().all() 

    return proxies

async def get_proxies_group(session: AsyncSession, user_id):
    stmt = select(Proxy.expired_at, func.count(Proxy.id)).where(Proxy.user_id==user_id).group_by(Proxy.expired_at)
    results: Result = await session.execute(stmt)
         
    return [{"expired_at": result[0], "count": result[1]} for result in results.all()]

async def get_expired_at_proxies(session: AsyncSession, user_id: int):
    stmt = select(Proxy.expired_at).where(Proxy.user_id == user_id)
    results: Result = await session.execute(stmt)
    proxies = results.scalars().all() 

    return proxies

async def get_list_proxy_group_date(user_id, session: AsyncSession):
    return await get_proxies_group(session=session, user_id=user_id)

async def get_proxy_by_date(date: str, user_id: int, session: AsyncSession):
    date = check_correct_date(date)
    proxies = await get_proxies(date=date, user_id=user_id, session=session)

    if proxies == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет прокси с такой датой | Unknown date for proxy"
        )

    return proxies

async def delete_proxy(date: str, user_id: int, session: AsyncSession):
    date = check_correct_date(date)
    stmt = select(Proxy).where(Proxy.expired_at==date).where(Proxy.user_id==user_id)
    result: Result = await session.execute(stmt)
    proxies = result.scalars().all()
    for proxy in proxies:
        await session.delete(proxy)
    await session.commit()
    
    return await get_proxies_group(user_id=user_id, session=session)

def validate_data_proxy_saving(proxy, user_id):
    proxy_http = f"http://{proxy[4]}:{str(int(proxy[5]))}"
    proxy_save = ProxySchemas(expired_at=proxy[0], login=proxy[2], password=proxy[3], ip_with_port=proxy_http, user_id=user_id)
    if not (str(proxy[1]) == 'nan'):
        proxy_save.id_proxy = str(proxy[1])
    proxy_for_save = Proxy(**proxy_save.model_dump())

    return proxy_for_save

async def save_proxy_to_db_from_file(file: UploadFile, user_id: int, session: AsyncSession):
    check_format(filename=file.filename)

    file_location = await save_file(file=file)
    check_same_file(filename=file.filename)
    data = await get_data(file_location=file_location)

    for proxy in data:
        if all([str(is_nan) == 'nan' for is_nan in proxy]):
            break
        
        proxy_for_save = validate_data_proxy_saving(proxy, user_id)
        
        session.add(proxy_for_save)
    await session.commit()

    return await get_list_proxy_group_date(user_id=user_id, session=session)

async def add_proxy(pre: dict, session: AsyncSession, user_id: int):
    proxies = pre["list"]
    for id_proxy in proxies:
        proxy = proxies[id_proxy]
        proxy_for_save = validate_data_proxy_saving([proxy["date_end"], proxy["id"], proxy["user"], proxy["pass"], proxy["host"], proxy["port"]], user_id=user_id)

        session.add(proxy_for_save)
    await session.commit()

async def buy_proxy(session: AsyncSession, user_id: int, count: int, duration: int):
    API_KEY = settings.proxy.API_KEY
    url = f"{settings.proxy.URL}{API_KEY}/buy?count={count}&period={duration}&country=ru&version=4"
    resp = requests.get(url)
    pre = json.loads(resp.text)
    if resp.status_code == 200 and pre['status'] == 'yes':
        await add_proxy(pre=pre, session=session, user_id=user_id)
        return await get_list_proxy_group_date(user_id=user_id, session=session)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Невозможно купить прокси'
    )

async def get_proxy_by_expired(session: AsyncSession, user_id: int, date: str, count: int):
    date = check_correct_date(date=date)
    stmt = select(Proxy).where(Proxy.user_id==user_id, Proxy.expired_at==date).order_by(Proxy.expired_at)
    result: Result = await session.execute(stmt)
    return result.scalars().all()[:count]

async def update_date_proxy(session: AsyncSession, user_id: int, date: str, count: int, duration: int):
    proxies = await get_proxy_by_expired(session=session, user_id=user_id, date=date, count=count)
    for proxy in proxies:
        proxy.is_using = True
        proxy.expired_at += datetime.timedelta(days=duration)
        session.add(proxy)
    await session.commit()

async def prolong_proxy(session: AsyncSession, user_id: int, count: int, duration: int, date: str):
    proxies = await get_proxy_by_expired(session=session, count=count, user_id=user_id, date=date)
    API_KEY = settings.proxy.API_KEY
    url = f"{settings.proxy.URL}{API_KEY}/prolong?period={duration}&ids={','.join([str(proxy.id_proxy) for proxy in proxies])}"
    pre = json.loads(requests.get(url).text)
    if pre["status"] == "yes":
        await update_date_proxy(session=session, user_id=user_id, date=date, count=count, duration=duration)
        return await get_list_proxy_group_date(user_id=user_id, session=session) 
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Невозможно продлить прокси"
    )