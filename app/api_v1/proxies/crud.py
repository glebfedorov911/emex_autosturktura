from fastapi import HTTPException, status

from core.config import settings
from core.models import Proxy
from .depends import not_enough_money, check_correct_date
from .schemas import ProxySchemas

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.sql import func

import requests
import json
import datetime


async def check_balance():
    url = settings.proxy.URL + f"/dev-api/balance/{settings.proxy.API_KEY}"

    return {
        "balance": dict(json.loads(requests.get(url).text))["balance"]
    }
    
async def buy_proxy(count: int = 1, duration: int = 30):
    url = settings.proxy.URL + f"/dev-api/buy-proxy/{settings.proxy.API_KEY}"

    data = {
        "PurchaseBilling": {
            "count": count,
            "duration": duration,
            "type": 100,
            "country": "ru"
        }
    }

    response = dict(json.loads(requests.post(url, json=data).text))
    
    not_enough_money(response=response)

async def add_proxy_to_database(user_id: int, count: int, session: AsyncSession):
    url = settings.proxy.URL + f"/dev-api/list/{settings.proxy.API_KEY}"

    data = {
        "type": "ipv4",
        "proxy_type": "server",
        "page": 1,
        "page_size": count,
        "sort": 0
    }

    response = dict(json.loads(requests.post(url, json=data).text))
    proxies = response["list"]["data"]

    proxy_in_db = []

    for proxy in proxies:
        ip_with_port = proxy["ip"] + proxy["http_port"]
        expired_at = datetime.datetime.strptime(proxy["expired_at"].split(" ")[0], '%Y-%m-%d').date()
        proxy_add = ProxySchemas(id_proxy=proxy["id"], login=proxy["login"], password=proxy["password"], ip_with_port=ip_with_port, expired_at=expired_at, user_id=user_id)
        
        new_proxy = Proxy(**proxy_add.model_dump())
        session.add(new_proxy)
        await session.commit()

        proxy_in_db.append(proxy_add)

    return proxy_in_db

async def get_list_proxy_group_date(user_id, session: AsyncSession):
    stmt = select(Proxy.expired_at, func.count(Proxy.id)).where(Proxy.user_id==user_id).group_by(Proxy.expired_at)
    results: Result = await session.execute(stmt)
         
    return [{"expired_at": result[0], "count": result[1]} for result in results.all()]

async def get_proxy_by_date(date: str, user_id: int, session: AsyncSession):
    date = check_correct_date(date)
    stmt = select(Proxy).where(Proxy.expired_at == date).where(Proxy.user_id == user_id)
    results: Result = await session.execute(stmt)
    proxies = results.scalars().all() 

    if proxies == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Нет прокси с такой датой | Unknown date for proxy"
        )

    return proxies

async def prolong_proxy(date: str, count: int, duration: int, user_id: int, session: AsyncSession):
    url = settings.proxy.URL + f"/dev-api/prolong/{settings.proxy.API_KEY}"

    date = check_correct_date(date)
    stmt = select(Proxy.id_proxy).where(Proxy.user_id==user_id).where(Proxy.expired_at==date)
    result: Result = await session.execute(stmt)

    id_list = [str(i) for i in result.scalars().all()]
    ids = ', '.join(id_list[:count])

    data = {
        "ProlongationForm": {
            "duration": duration,
            "proxies": ids
        }
    }

    response = dict(json.loads(requests.post(url, json=data).text))

    not_enough_money(response=response)

    return {
        "message": "Вы успешно продлили прокси | Success prolong proxies"
    }
        
