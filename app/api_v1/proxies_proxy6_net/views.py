from fastapi import APIRouter, Depends, UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.api_v1.auth.utils import get_payload
from app.api_v1.utils.depends import get_shablon as gs
from app.core.config import settings
from . import crud

import requests
import json


router = APIRouter(prefix="/proxies", tags=["Proxies2"])

@router.post("/upload_file_with_proxy")
async def upload_proxy_from_file(session: AsyncSession = Depends(db_helper.session_depends), file: UploadFile = File(...), payload = Depends(get_payload)):
    return await crud.save_proxy_to_db_from_file(file=file, user_id=payload.get("sub"), session=session)

@router.get("/get_proxy_group")
async def get_list_proxy_group_date(payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends)):

    return await crud.get_list_proxy_group_date(session=session, user_id=payload["sub"])

@router.get("/get_proxy_by_date") #2024-09-23 - date example
async def get_proxy_by_date(date: str = "1970-01-01T00:00:00", session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    '''
    date - дата окончания прокси
    '''

    return await crud.get_proxy_by_date(date=date, session=session, user_id=payload["sub"])

@router.delete("/delete_proxy_group")
async def delete_proxy(date: str = "1970-01-01T00:00:00", payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends)):
    return await crud.delete_proxy(date=date, user_id=payload.get("sub"), session=session)

@router.get("/get_shablon")
async def get_shablon():
    return await gs(settings.proxy.path_for_upload)

@router.get("/buy_proxy")
async def buy_proxy(payload = Depends(get_payload), count: int = 1, duration: int = 30, session: AsyncSession = Depends(db_helper.session_depends)):
    return await crud.buy_proxy(session=session, user_id=payload.get("sub"), count=count, duration=duration)

@router.get("/prolong_proxy")
async def prolong_proxy(payload = Depends(get_payload), count: int = 1, duration: int = 30, date: str = "1970-01-01T00:00:00", session: AsyncSession = Depends(db_helper.session_depends)):
    return await crud.prolong_proxy(session=session, count=count, user_id=payload.get("sub"), duration=duration, date=date)

@router.get("/get_balance_bright_data")
async def get_balance_bright_data():
    headers = {'Authorization': f'Bearer {settings.proxy.BRIGHT_DATA_TOKEN}'}
    r = requests.get('https://api.brightdata.com/customer/balance', headers=headers)
    return json.loads(r.content)