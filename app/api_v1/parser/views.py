from fastapi import WebSocket, APIRouter, Request, Depends, Response, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from threading import Event, Thread
from datetime import datetime

from app.core.config import settings
from app.core.models import db_helper
from app.api_v1.users.crud import get_payload
from .depends import run, user_data, create, split_file_for_thr, not_in_user_data
from . import crud

import asyncio
import pandas as pd
import os


router = APIRouter(prefix="/parser", tags=["Parser"])

count_of_thread = 4

templates = Jinja2Templates(directory=settings.templates.templates_path)

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="test.html"
    )

@router.get("/start/")
async def start_threadings(session: AsyncSession = Depends(db_helper.session_depends), payload = Depends(get_payload)):
    proxies = await crud.get_proxies(payload.get("sub"), session=session)

    global user_data
    
    if not os.path.exists(str(settings.upload.path_for_upload) + '/' + await crud.get_last_upload_files(session=session, user_id=payload.get("sub"))):
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Вы не загрузили не одного файла"
        )

    df = pd.read_excel(str(settings.upload.path_for_upload) + '/' + await crud.get_last_upload_files(session=session, user_id=payload.get("sub"))) # ИЗ БД

    df = df.apply(lambda col: col.astype(object))
    df_to_list = df.values.tolist()
    brands, nums = create(df_to_list)

    user_data[payload.get("sub")] = {"proxies": proxies.copy(), "atms_proxy": {}, "ban_list": [], "total": 0, "proxies_count": len(proxies), "all_data": [],
    "threads": [None] * count_of_thread, "events": [Event() for _ in range(count_of_thread)], "len_brands": len(brands), "status": "Парсер запущен", "filter_id": 0}

    brands_split = split_file_for_thr(count_of_thread, brands)
    nums_split = split_file_for_thr(count_of_thread, nums)
    messages = []

    # await main(brands_split[0], nums_split[0], payload.get("sub"))

    for index in range(count_of_thread):
        if user_data[payload.get("sub")]["threads"][index] is None or not user_data[payload.get("sub")]["threads"][index].is_alive():
            user_data[payload.get("sub")]["events"][index].clear()
            user_data[payload.get("sub")]["threads"][index] = Thread(target=run, args=(brands_split[index], nums_split[index], payload.get("sub")))
            user_data[payload.get("sub")]["threads"][index].start()
            messages.append("старт")
        else:
            messages.append("уже началось")

    return JSONResponse(content=messages)

@router.get("/stop/")
async def stop_threadings(payload=Depends(get_payload)):
    global user_data
    not_in_user_data(payload)

    for index in range(count_of_thread):
        user_data[payload.get("sub")]["events"][index].set()

    user_data[payload.get("sub")]["all_data"] = []
    user_data[payload.get("sub")]["status"] = "Вы остановили парсер"
    
    return JSONResponse(content={"message": "все потоки прекращены"})

@router.get("/status_check/")
async def status_threadings(payload = Depends(get_payload)):
    global user_data
    not_in_user_data(payload)

    return JSONResponse(content={"user_data": user_data[payload.get("sub")]["all_data"], "ban": user_data[payload.get("sub")]["ban_list"]})

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, payload=Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends)):
    global user_data
    await websocket.accept()

    while True:
        if payload.get("sub") in user_data:
            len_ban = len(user_data[payload.get("sub")]["ban_list"])
            proxies = user_data[payload.get("sub")]["proxies_count"]
            len_all_data = len(user_data[payload.get("sub")]["all_data"])
            len_brands = user_data[payload.get("sub")]["len_brands"]

            await websocket.send_json({
                "ban_proxies": round(len_ban/proxies, 2)*100,
                "full": round(len_all_data/len_brands, 2)*100
            })

            if round(len_all_data/len_brands, 2)*100 == 100.0:
                user_data[payload.get("sub")]["status"] = "Парсер закончил работу"
                
                df = pd.DataFrame(user_data[payload.get("sub")]["all_data"], columns=["Артикул", "Номер товара", "Лого", "Доставка", "Лучшая цена"])
                last_file = await crud.get_last_upload_files(session=session, user_id=payload.get("sub"))
                filename = f'{payload.get("username")}_послепарсинга_{last_file.split("_")[-1]}'
                if not os.path.exists(str(settings.upload.path_for_upload) + '/' + filename):
                    df.to_excel(str(settings.upload.path_for_upload) + '/' + filename, index=False)  
                    await crud.add_after_parsing_file(user_id=payload.get("sub"), session=session, new_data={"after_parsing_filename": filename, "finish_date": datetime.now(), "filter_id": 
                        user_data[payload.get("sub")]["filter_id"]})
                for index in range(count_of_thread):
                    user_data[payload.get("sub")]["events"][index].set()   

            if  round(len_all_data/len_brands, 2)*100 == 0.0 and not user_data[payload.get("sub")]["threads"][0].is_alive():
                user_data[payload.get("sub")]["status"] = "Парсер не запущен"

            await asyncio.sleep(2)
        else:
            await websocket.send_json({
                "message": "запустите парсер"
            })

@router.websocket("/ws/status/")
async def websocket_endpoint(websocket: WebSocket, payload=Depends(get_payload)):
    global user_data
    await websocket.accept()
    while True:
        if payload.get("sub") in user_data:
            await websocket.send_json({"status": user_data[payload.get("sub")]["status"]})
        else:
            await websocket.send_json({"status": "Парсер не запущен"})
    