from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from sqlalchemy import select
from sqlalchemy.sql import func

from app.core.models import Proxy

import datetime


def not_enough_money(response):
    if not response["success"]:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="У вас недостаточно средств | You haven't got enough money"
        )

def check_correct_date(date):
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Некорректная дата | Incorrect date"
        )
    
    return date

async def get_proxies(session: AsyncSession, date, user_id):
    stmt = select(Proxy).where(Proxy.expired_at == date).where(Proxy.user_id == user_id)
    results: Result = await session.execute(stmt)
    proxies = results.scalars().all() 

    return proxies

async def get_proxies_group(session: AsyncSession, user_id):
    stmt = select(Proxy.expired_at, func.count(Proxy.id)).where(Proxy.user_id==user_id).group_by(Proxy.expired_at)
    results: Result = await session.execute(stmt)
         
    return [{"expired_at": result[0], "count": result[1]} for result in results.all()]