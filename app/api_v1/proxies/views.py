from fastapi import APIRouter, Cookie, HTTPException, status, Depends, Header

from sqlalchemy.ext.asyncio import AsyncSession

from . import crud
from app.api_v1.users.crud import get_payload
from app.api_v1.auth.depends import check_payload
from app.core.models import db_helper


router = APIRouter(prefix="/proxies", tags=["Proxies"])

@router.get("/get_balance")
async def get_balance(access_token: str | None = Header(default=None, convert_underscores=False)):
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Вы не авторизованы | You are not auth"
        )

    payload = await check_payload(access_token=access_token)

    return await crud.check_balance()

@router.get("/buy_proxy")
async def buy_proxy(access_token: str | None = Header(default=None, convert_underscores=False), count: int = 1, duration: int = 30, session: AsyncSession = Depends(db_helper.session_depends)):
    '''
    count - количество прокси
    duration - срок
    '''

    payload = await check_payload(access_token=access_token)

    await crud.buy_proxy(count, duration)

    return await crud.add_proxy_to_database(payload["sub"], count=count, session=session)

@router.get("/get_proxy_group")
async def get_list_proxy_group_date(access_token: str | None = Header(default=None, convert_underscores=False), session: AsyncSession = Depends(db_helper.session_depends)):
    payload = await check_payload(access_token=access_token)

    return await crud.get_list_proxy_group_date(session=session, user_id=payload["sub"])

@router.get("/get_proxy_by_date/") #2024-09-23 - date example
async def get_proxy_by_date(date: str = "1970-01-01", session: AsyncSession = Depends(db_helper.session_depends), access_token: str | None = Header(default=None, convert_underscores=False)):
    '''
    date - дата окончания прокси
    '''
    payload = await check_payload(access_token=access_token)

    return await crud.get_proxy_by_date(date=date, session=session, user_id=payload["sub"])

@router.get("/prolong_proxy")
async def prolong_proxy(date: str = "1970-01-01", count: int = 1000, duration: int = 30, access_token: str | None = Header(default=None, convert_underscores=False), session: AsyncSession = Depends(db_helper.session_depends)):
    '''
    date - дата окончания прокси
    count - количество прокси которые будет продлено
    duration - cрок продления
    '''
    payload = await check_payload(access_token=access_token)

    return await crud.prolong_proxy(date=date, count=count, duration=duration, user_id=payload.get("sub"), session=session)


