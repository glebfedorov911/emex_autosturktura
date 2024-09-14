from fastapi import (
    APIRouter,
    Request,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    status,
    Depends,
    Header
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from threading import Thread, Event
from datetime import datetime

from app.core.config import settings
from app.core.models import db_helper
from app.api_v1.auth.utils import get_payload
from app.api_v1.files.depends import get_unique_filename
from app.api_v1.utils.depends import edit_file 

from . import crud
from .parser import user_data, run
from .depends import *

import asyncio
import time
import random
import pandas as pd

# ДОПИСАТЬ СОХРАНЕНИЕ#

router = APIRouter(prefix="/new_parser", tags=["New Parser"])
templates = Jinja2Templates(directory=settings.templates.templates_path)

count_of_threadings = 6
threads: list[Thread] = [None] * count_of_threadings


@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(request=request, name="test2.html")


@router.websocket("/websocket_percent/{access_token}")
async def websocket_endpoint(
    websocket: WebSocket,
    access_token: str,
    session: AsyncSession = Depends(db_helper.session_depends),
):
    global user_data

    payload = await check_payload(access_token=access_token)

    # files = f'{payload.get("username")}_дляпарсинг.xlsx'
    # files = get_unique_filename(str(settings.upload.path_for_upload), files)
    if not payload.get("sub") in user_data:
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
    else:
        if not "threads" in user_data[payload.get("sub")]:
            user_data[payload.get("sub")] = {
                "excel_result": [],
                "status": "PARSER_NOT_STARTED_DATA_SAVED",
                "count_proxies": 1,
                "ban_list": set(),
                "count_brands": 1,
                "threads": threads.copy(),
                "start_file": None,
                "flag": True,
            }

    await websocket.accept()
    try:
        while True:
            ud = user_data[payload.get("sub")]
            if ud["count_proxies"] == 0:
                ud["count_proxies"] = 1
                ud["status"] = "Закончились прокси"
            # if ud["start_file"] is None:
                # files = f'{payload.get("username")}_дляпарсинг.xlsx'
                # files = get_unique_filename(str(settings.upload.path_for_upload), files)
                # ud["start_file"] = files

            await websocket.send_json(
                {
                    "Percent_parsing_goods": int(
                        len(ud["excel_result"]) / ud["count_brands"] * 100
                    ),
                    "Percent_banned_list": int(
                        len(ud["ban_list"]) / ud["count_proxies"] * 100
                    ),
                    # "Start_file": files,
                }
            )
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        await websocket.close()


@router.websocket("/websocket_status/{access_token}")
async def websocket_status_endpoint(
    websocket: WebSocket,
    access_token: str,
    session: AsyncSession = Depends(db_helper.session_depends),
):
    global user_data
    
    payload = await check_payload(access_token=access_token)
    
    await crud.unbanned_proxy(session=session, user_id=payload.get("sub"))
    await crud.delete_proxy_banned(session=session, user_id=payload.get("sub"))
    if not payload.get("sub") in user_data:
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
    else:
        if not "threads" in user_data[payload.get("sub")]:
            user_data[payload.get("sub")] = {
                "excel_result": [],
                "status": "PARSER_NOT_STARTED_DATA_SAVED",
                "count_proxies": 1,
                "ban_list": set(),
                "count_brands": 1,
                "threads": threads.copy(),
                "start_file": None,
                "flag": True,
            }


    await websocket.accept()
    try:
        while True:
            ud = user_data[payload.get("sub")]
            # asyncio.sleep(10)
            await websocket.send_json({"Status": ud["status"]})
            if (
                int(len(ud["excel_result"]) / ud["count_brands"] * 100) == 100
                and not ud["flag"]
            ):
                ud["status"] = "PARSING_COMPLETED"
                ud["flag"] = True
            elif (
                int(len(ud["ban_list"]) / ud["count_proxies"] * 100) == 100
                and not ud["flag"]
            ):
                ud["status"] = "ALL_PROXIES_BANNED"
                ud["flag"] = True
            elif any([thread is None for thread in ud["threads"]]) or not any(
                [thread.is_alive() for thread in ud["threads"]]
            ):
                ud["status"] = "Парсер не запущен"
                if ud["flag"]:
                    ud["status"] = "PARSER_NOT_STARTED_DATA_SAVED"
                    ud["excel_result"] = []
                    ud["ban_list"] = []
                if await check_after_parsing_file(session=session, user_id=payload.get("sub")) and ud["flag"]:
                    ud["flag"] = False
                    ud["status"] = "Парсер не запущен"
            else:
                ud["status"] = "PARSER_RUNNING"
            
            if ud["status"] in (
                "ALL_PROXIES_BANNED",
                "PARSING_COMPLETED",
            ):
                file_name_last = (await crud.get_last_upload_files(user_id=payload.get("sub"), session=session)).before_parsing_filename
                result_file_name = f"{file_name_last.split('.')[0]}_после_парсинга_{random.randint(1, 10000000000000000)}.xlsx"

                df = pd.DataFrame(ud["excel_result"], columns=user_data[payload.get("sub")]['columns'])
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
                await edit_file(str(settings.upload.path_for_upload) + "/" + result_file_name, ["K", "J", "L", "M", "F"])
                await crud.saving_to_table_data(
                    user_id=payload.get("sub"), session=session, data=ud["excel_result"], filename=result_file_name
                )
                await crud.set_parsing(session=session, status=False, user_id=payload.get("sub"))
                await crud.set_banned_proxy(
                    proxy_servers=ud["ban_list"], session=session, user_id=payload.get("sub")
                )
                user_data[payload.get("sub")]["threads"] = [None] * count_of_threadings
            if ud["status"] == "Парсер не запущен":
                if payload.get("sub") in user_data:
                    user_data[payload.get("sub")]['ban_list'] = []
                    user_data[payload.get("sub")]['excel_result'] = []

            await asyncio.sleep(3)
    except WebSocketDisconnect:
        await websocket.close()


@router.get("/start/{filter_id}")
async def start(
    filter_id: int,
    payload = Depends(get_payload),
    session: AsyncSession = Depends(db_helper.session_depends),
):
    global user_data
    

    messages = []
    user_id = payload.get("sub")
    proxies = await crud.get_proxies(session=session, user_id=payload.get("sub"))
    filter = await crud.get_filter(
        session=session, user_id=payload.get("sub"), filter_id=filter_id
    )
    try:
        files = (
            await crud.get_last_upload_files(user_id=user_id, session=session)
        ).before_parsing_filename
    except:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Файл уже был спаршен"
        )

    if all( [user_data[user_id]["threads"][i] is None or not user_data[user_id]["threads"][i].is_alive() for i in range(count_of_threadings)] ):
        user_data[payload.get("sub")] = {
            "threads": threads.copy(),
            "events": [Event() for _ in range(count_of_threadings)],
            "proxies": proxies,
            "filter": filter,
            "excel_result": [],
            "status": "PARSER_RUNNING",
            "count_proxies": len(set(proxies)),
            "ban_list": set(),
            "count_brands": 1,
            "filter_id": filter_id,
            "flag": False,
            # "start_file": files,
        }

    if proxies == []:
        user_data[payload.get("sub")]["status"] = "Закончились прокси"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="прокси закончились"
        )
    elif files is None:
        user_data[payload.get("sub")]["status"] = "Данный файл уже спаршен либо не загружен"
        return JSONResponse("Данный файл уже спаршен")
    elif filter is None:
        user_data[payload.get("sub")]["status"] = "Неизвестный фальтр"
        return JSONResponse("Неизвестный фальтр")
    else:
        await crud.set_parsing(session=session, status=True, user_id=payload.get("sub"))
        
        df = pd.read_excel(str(settings.upload.path_for_upload) + "/" + files)

        df = df.apply(lambda col: col.astype(object))
        df_to_list = df.values.tolist()
        brands= create(df_to_list)
        user_data[user_id]["count_brands"] = len(brands)

        brands = split_file_for_thr(count_of_threadings, brands)
        user_data[user_id]["threads"] = user_data[user_id]["threads"][: len(brands)]
        for index in range(len(brands)):
            if (
                user_data[user_id]["threads"][index] is None
                or not user_data[user_id]["threads"][index].is_alive()
            ):
                user_data[user_id]["events"][index].clear()
                user_data[user_id]["threads"][index] = Thread(
                    target=run, args=(brands[index], user_id)
                )
                user_data[user_id]["threads"][index].start()
                messages.append(f"поток {index+1} запущен")
            else:
                messages.append(f"поток {index+1} уже запущен")

        return JSONResponse(messages)


@router.get("/stop")
async def stop(payload = Depends(get_payload)):
    global user_data

    user_id = payload.get("sub")
    for index in range(count_of_threadings):
        user_data[user_id]["events"][index].set()

    return JSONResponse(content="Парсер останавливается")