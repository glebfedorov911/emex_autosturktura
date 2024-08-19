from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from threading import Thread, Event

from app.core.config import settings
from app.core.models import db_helper
from app.api_v1.users.crud import get_payload
from . import crud
from .parser import user_data, run
from .depends import *

import asyncio
import time
import pandas as pd
#ДОПИСАТЬ СОХРАНЕНИЕ

router = APIRouter(prefix="/new_parser", tags=["New Parser"])
templates = Jinja2Templates(directory=settings.templates.templates_path)

count_of_threadings = 4 
threads: list[Thread] = [None] * count_of_threadings

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="test2.html"
    )

@router.websocket("/ws2/{filter_id}")
async def websocket_endpoint(filter_id: int, websocket: WebSocket, payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.get_scoped_session)):
    global user_data

    proxies = await crud.get_proxies(session=session, user_id=payload.get("sub"))
    filter = await crud.get_filter(session=session, user_id=payload.get("sub"), filter_id=filter_id)
    user_data[payload.get("sub")] = {"threads": threads.copy(), "events": [Event() for _ in range(count_of_threadings)], 
                                     "proxies": proxies, "filter": filter, "excel_result": [], "status": "Парсер не запущен",
                                     "count_proxies": len(proxies), "ban_list": set(), "count_brands": 1}
    await websocket.accept()
    flag = False
    try:
        while True:
            # await websocket.send_json({"excel_result": user_data[payload.get("sub")]["excel_result"], "ban_list": list(user_data[payload.get("sub")]["ban_list"])})
            ud = user_data[payload.get("sub")]
            await websocket.send_json({"Проценты спаршенных товаров": int(len(ud["excel_result"])/ud["count_brands"]*100),
                                       "Процент забаненных прокси": int(len(ud["ban_list"])/ud["count_proxies"]*100),
                                       "Статус": ud["status"]})
            if flag:
                ud["status"] = "Всё сохранено"
            if int(len(ud["excel_result"])/ud["count_brands"]*100) == 100 and not flag:
                ud["status"] = "Товары спаршены, подождите, идет сохранение"
                flag=True
            elif int(len(ud["ban_list"])/ud["count_proxies"]*100) == 100 and not flag:
                ud["status"] = "Все прокси забанены, подождите, идет редактирование"
                flag=True
            elif any([thread is None for thread in ud["threads"]]) or not any([thread.is_alive() for thread in ud["threads"]]):
                ud["status"] = "Парсер не запущен"
            else:
                ud["status"] = "Парсер работает"
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await websocket.close()

@router.get("/start")
async def start(payload=Depends(get_payload), session: AsyncSession = Depends(db_helper.get_scoped_session)):
    global user_data

    messages = []
    user_id = payload.get("sub")
    files = await crud.get_last_upload_files(user_id=user_id, session=session)
    df = pd.read_excel(str(settings.upload.path_for_upload) + '/' + files)

    df = df.apply(lambda col: col.astype(object))
    df_to_list = df.values.tolist()
    brands, nums = create(df_to_list)
    user_data[user_id]["count_brands"] = len(brands)

    brands, nums = split_file_for_thr(count_of_threadings, brands), split_file_for_thr(count_of_threadings, nums)
    user_data[user_id]["threads"] = user_data[user_id]["threads"][:len(brands)]
    for index in range(len(brands)):
        if user_data[user_id]["threads"][index] is None or not user_data[user_id]["threads"][index].is_alive():
            user_data[user_id]["events"][index].clear()
            user_data[user_id]["threads"][index] = Thread(target=run, args=(brands[index], nums[index], user_id))
            user_data[user_id]["threads"][index].start()
            messages.append(f"поток {index+1} запущен")
        else:
            messages.append(f"поток {index+1} уже запущен")

    return JSONResponse(messages)

@router.get("/stop")        
async def stop(payload=Depends(get_payload)):
    global user_data

    user_id = payload.get("sub")
    for index in range(count_of_threadings):
        user_data[user_id]["events"][index].set()
    ud["status"] = "Парсер остановлен"
    return JSONResponse(content="Потоки остановлены")