from fastapi import (
    APIRouter,
    Request,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    status,
    Depends,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from threading import Thread, Event

from app.core.config import settings
from app.core.models import db_helper
from app.api_v1.users.crud import get_payload
from . import crud
from .parser import user_data, run, columns
from .depends import *

import asyncio
import time
import pandas as pd

# ДОПИСАТЬ СОХРАНЕНИЕ

router = APIRouter(prefix="/new_parser", tags=["New Parser"])
templates = Jinja2Templates(directory=settings.templates.templates_path)

count_of_threadings = 4
threads: list[Thread] = [None] * count_of_threadings


@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(request=request, name="test2.html")


@router.websocket("/websocket_percent")
async def websocket_endpoint(
    websocket: WebSocket,
    payload=Depends(get_payload),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    global user_data

    files = (
        await crud.get_last_upload_files(user_id=payload.get("sub"), session=session)
    ).before_parsing_filename

    user_data[payload.get("sub")] = {
        "excel_result": [],
        "status": "Парсер не запущен",
        "count_proxies": 1,
        "ban_list": set(),
        "count_brands": 1,
        "threads": threads.copy(),
        "start_file": files,
        "flag": False,
    }
    await websocket.accept()
    try:
        while True:
            ud = user_data[payload.get("sub")]
            await websocket.send_json(
                {
                    "Percent_parsing_goods": int(
                        len(ud["excel_result"]) / ud["count_brands"] * 100
                    ),
                    "Percent_banned_list": int(
                        len(ud["ban_list"]) / ud["count_proxies"] * 100
                    ),
                    "Start_file": ud["start_file"],
                }
            )
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        await websocket.close()


@router.websocket("/websocket_status")
async def websocket_status_endpoint(
    websocket: WebSocket,
    payload=Depends(get_payload),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    global user_data

    await websocket.accept()
    user_data[payload.get("sub")] = {
        "excel_result": [],
        "status": "Парсер не запущен",
        "count_proxies": 1,
        "ban_list": set(),
        "count_brands": 1,
        "threads": threads.copy(),
        "start_file": None,
        "flag": False,
    }
    files = (
        await crud.get_last_upload_files(user_id=payload.get("sub"), session=session)
    ).before_parsing_filename
    result_file_name = (
        payload.get("username") + "_послепарсинга_" + files.split("_")[-1]
    )
    try:
        while True:
            ud = user_data[payload.get("sub")]
            # asyncio.sleep(10)
            await websocket.send_json({"Status": ud["status"]})
            if (
                int(len(ud["excel_result"]) / ud["count_brands"] * 100) == 100
                and not ud["flag"]
            ):
                ud["status"] = "Товары спаршены, подождите, идет сохранение"
                ud["flag"] = True
            elif (
                int(len(ud["ban_list"]) / ud["count_proxies"] * 100) == 100
                and not ud["flag"]
            ):
                ud["status"] = "Все прокси забанены, подождите, идет редактирование"
                ud["flag"] = True
            elif any([thread is None for thread in ud["threads"]]) or not any(
                [thread.is_alive() for thread in ud["threads"]]
            ):
                ud["status"] = "Парсер не запущен"
                if ud["flag"]:
                    ud["status"] = "Парсер не запущен | Данные сохранены"
            else:
                ud["status"] = "Парсер работает"

            if ud["status"] in (
                "Все прокси забанены, подождите, идет редактирование",
                "Товары спаршены, подождите, идет сохранение",
            ):
                df = pd.DataFrame(ud["excel_result"], columns=columns)
                await crud.add_final_file_to_table(
                    user_id=payload.get("sub"),
                    session=session,
                    result_name=result_file_name,
                    filter_id_global=ud["filter_id"],
                )
                df.to_excel(
                    str(settings.upload.path_for_upload) + "/" + result_file_name,
                    index=False,
                )
                await crud.saving_to_table_data(
                    user_id=payload.get("sub"), session=session, data=ud["excel_result"]
                )
                await crud.set_banned_proxy(
                    proxy_servers=ud["ban_list"], session=session
                )
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        await websocket.close()


@router.get("/start/{filter_id}")
async def start(
    filter_id: int,
    payload=Depends(get_payload),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    global user_data

    messages = []
    user_id = payload.get("sub")
    proxies = await crud.get_proxies(session=session, user_id=payload.get("sub"))
    filter = await crud.get_filter(
        session=session, user_id=payload.get("sub"), filter_id=filter_id
    )
    files = (
        await crud.get_last_upload_files(user_id=user_id, session=session)
    ).before_parsing_filename
    user_data[payload.get("sub")] = {
        "threads": threads.copy(),
        "events": [Event() for _ in range(count_of_threadings)],
        "proxies": proxies,
        "filter": filter,
        "excel_result": [],
        "status": "Парсер не запущен",
        "count_proxies": len(proxies),
        "ban_list": set(),
        "count_brands": 1,
        "filter_id": filter_id,
        "flag": False,
        "start_file": files,
    }

    df = pd.read_excel(str(settings.upload.path_for_upload) + "/" + files)

    df = df.apply(lambda col: col.astype(object))
    df_to_list = df.values.tolist()
    brands, nums = create(df_to_list)
    user_data[user_id]["count_brands"] = len(brands)

    brands, nums = split_file_for_thr(count_of_threadings, brands), split_file_for_thr(
        count_of_threadings, nums
    )
    user_data[user_id]["threads"] = user_data[user_id]["threads"][: len(brands)]
    for index in range(len(brands)):
        if (
            user_data[user_id]["threads"][index] is None
            or not user_data[user_id]["threads"][index].is_alive()
        ):
            user_data[user_id]["events"][index].clear()
            user_data[user_id]["threads"][index] = Thread(
                target=run, args=(brands[index], nums[index], user_id)
            )
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

    return JSONResponse(content="Парсер останавливается")
