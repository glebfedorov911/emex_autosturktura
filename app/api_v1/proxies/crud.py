from fastapi import HTTPException, status

from app.core.config import settings
from app.core.models import Proxy
from .depends import not_enough_money, check_correct_date, get_proxies, get_proxies_group
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
        ip_with_port = "http://" + proxy["ip"] + ":" + proxy["http_port"]
        expired_at = datetime.datetime.strptime(proxy["expired_at"].split(" ")[0], '%Y-%m-%d').date()
        proxy_add = ProxySchemas(id_proxy=proxy["id"], login=proxy["login"], password=proxy["password"], ip_with_port=ip_with_port, expired_at=expired_at, user_id=user_id)
        
        new_proxy = Proxy(**proxy_add.model_dump())
        session.add(new_proxy)
        await session.commit()

    return await get_proxies_group(user_id=user_id, session=session)


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

async def prolong_proxy(date: str, count: int, duration: int, user_id: int, session: AsyncSession):
    url = settings.proxy.URL + f"/dev-api/prolong/{settings.proxy.API_KEY}"

    date = check_correct_date(date)
    proxies = await get_proxies(session=session, date=date, user_id=user_id)
    
    id_list = [str(i.id_proxy) for i in proxies]
    ids = ', '.join(id_list[:count])

    if ids == '':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не найдены прокси | Not found proxies"
        )

    data = {
        "ProlongationForm": {
            "duration": duration,
            "proxies": ids
        }
    }

    response = dict(json.loads(requests.post(url, json=data).text))

    not_enough_money(response=response)
    proxies = await get_proxies(session=session, date=date, user_id=user_id)
    k = 0

    for proxy in proxies:
        if str(proxy.id_proxy) in ids.split(', '): 
            proxy.expired_at += datetime.timedelta(days=duration)
            await session.commit()
            k += 1
        
        if k == len(ids.split(", ")):
            break

    return await get_proxies_group(user_id=user_id, session=session)
        
