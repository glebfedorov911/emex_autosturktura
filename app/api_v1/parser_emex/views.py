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
from fastapi.responses import JSONResponse, FileResponse

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from threading import Thread, Event
from datetime import datetime

from app.core.config import settings
from app.core.models import db_helper
from app.core.models.proxy_bright_data import ProxyBrightData
from app.api_v1.auth.utils import get_payload
from app.api_v1.utils.depends import edit_file, get_unique_filename

from . import crud
from .parser_test_requests import user_data, run
from .depends import *
from .schemas import ProxyCountriesCreateSchemas

import asyncio
import time
import random
import os
import pandas as pd
import threading
import httpx
import requests
import json


# ДОПИСАТЬ СОХРАНЕНИЕ####

router = APIRouter(prefix="/new_parser", tags=["New Parser"])
templates = Jinja2Templates(directory=settings.templates.templates_path)

count_of_threadings = 32
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

    if not payload.get("sub") in user_data:
        user_data[payload.get("sub")] = {
            "excel_result": [],
            "status": "Парсер не запущен",
            "count_brands": 1,
            "threads": threads.copy(),
            "flag": False,
            "counter_parsered": 0,
            "using_proxy": None,
            "start": 0,
            "skip": 0,
            "proxies_id": []
        }
    else:
        if not "threads" in user_data[payload.get("sub")]:
            user_data[payload.get("sub")] = {
                "excel_result": [],
                "status": "PARSER_NOT_STARTED_DATA_SAVED",
                "count_brands": 1,
                "threads": threads.copy(),
                "flag": True,
                "counter_parsered": 0,
                "using_proxy": None,
                "start": 0,
                "skip": 0,
                "proxies_id": []
            }

    await websocket.accept()
    try:
        while True:
            for i in range(count_of_threadings):
                if user_data[payload.get("sub")]["status"] == "PARSER_RUNNING":
                    try:   
                        if (not user_data[payload.get("sub")]["threads"][i].is_alive()):
                            stmt = select(ProxyBrightData).where(ProxyBrightData.id.in_(user_data[payload.get("sub")]["proxies_id"]))
                            result = await session.execute(stmt)
                            result = result.scalars().all()

                            proxies = [
                                f"http://{i.login}:{i.password}@{i.address}:{i.port}"
                                for i in result]

                            user_data[payload.get("sub")]["events"][i].clear()
                            user_data[payload.get("sub")]["threads"][i] = Thread(
                                target=run, args=(payload.get("sub"), user_data[payload.get("sub")]["using_proxy"], i, proxies)
                            )
                            user_data[payload.get("sub")]["threads"][i].start()
                    except Exception as e:
                        print("-="*20)
                        print(e)

            ud = user_data[payload.get("sub")]
            if ud["count_brands"] == 0:
                ud["count_brands"] = 1
            await websocket.send_json(
                {
                    "Percent_parsing_goods": round(
                        ud["counter_parsered"] / ud["count_brands"] * 100, 2
                    ),
                }
            )

            await asyncio.sleep(3)
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        print("-="*20)
        print(e)


@router.websocket("/websocket_status/{access_token}")
async def websocket_status_endpoint(
    websocket: WebSocket,
    access_token: str,
    session: AsyncSession = Depends(db_helper.session_depends),
):
    global user_data
    
    payload = await check_payload(access_token=access_token)
    
    if not payload.get("sub") in user_data:
        user_data[payload.get("sub")] = {
            "excel_result": [],
            "status": "Парсер не запущен",
            "count_brands": 1,
            "threads": threads.copy(),
            "flag": False,
            "counter_parsered": 0,
            "using_proxy": None,
            "start": 0,
            "skip": 0,
            "proxies_id": []
        }
    else:
        if not "threads" in user_data[payload.get("sub")]:
            user_data[payload.get("sub")] = {
                "excel_result": [],
                "status": "PARSER_NOT_STARTED_DATA_SAVED",
                "count_brands": 1,
                "threads": threads.copy(),
                "flag": True,
                "counter_parsered": 0,
                "using_proxy": None,
                "start": 0,
                "skip": 0,
                "proxies_id": []
            }

    await websocket.accept()
    try:
        while True:
            ud = user_data[payload.get("sub")]
            await websocket.send_json({"Status": ud["status"]})
            # print(ud["counter_parsered"], ud["status"])
            # print(int(ud["counter_parsered"] / ud["count_brands"] * 100), ud["counter_parsered"])
            if (
                int(ud["counter_parsered"] / ud["count_brands"] * 100) >= 100
                and not ud["flag"]
            ):
                ud["status"] = "PARSING_COMPLETED"
                ud["flag"] = True
            elif any([thread is None for thread in ud["threads"]]) or not any(
                [thread.is_alive() for thread in ud["threads"]]
            ) and (int(ud["counter_parsered"] / ud["count_brands"] * 100) == 0):  
                if not "saving" in ud:
                    ud["status"] = "Парсер не запущен"
                    if ud["flag"]:
                        ud["status"] = "PARSER_NOT_STARTED_DATA_SAVED"
                        print("я был тут")
                    if await check_after_parsing_file(session=session, user_id=payload.get("sub")) and ud["flag"]:
                        ud["flag"] = False
                        ud["status"] = "Парсер не запущен"
            else:
                ud["status"] = "PARSER_RUNNING"
                ud["saving"] = True

            print("EXCEL_RESULT:", len(ud["excel_result"]))
            if (limit := len(ud["excel_result"][ud["skip"]:])) >= 350:
                ud["start"] = ud["skip"]
                ud["skip"] += limit
                print("СОХРАНЯЮ")
                print("Данные для сохранения 1:", ud["start"], ':', ud["skip"], len(ud["excel_result"]), "ПРОЦЕНТЫ:", int(ud["counter_parsered"] / ud["count_brands"] * 100))
                fileData = (await crud.get_last_upload_files(user_id=payload.get("sub"), session=session))
                await crud.saving_to_table_data(user_id=payload.get("sub"), session=session, data=ud["excel_result"][ud["start"]:ud["skip"]], file_id=fileData.id)
                print("Данные для сохранения 2:", ud["start"], ':', ud["skip"], len(ud["excel_result"]), "ПРОЦЕНТЫ:", int(ud["counter_parsered"] / ud["count_brands"] * 100))
            print("EXCEL_RESULT2:", len(ud["excel_result"]))
            if ud["status"] in (
                "ALL_PROXIES_BANNED",
                "PARSING_COMPLETED"
            ): 
                print("зашли в эту штуку") 
                try:
                    for i in range(count_of_threadings):
                        user_data[payload.get("sub")]["events"][i].clear()
                except:
                    pass
                try:
                    print("зашли в try") 
                    if "saving" in user_data[payload.get("sub")]:
                        del user_data[payload.get("sub")]["saving"]
                    user_data[payload.get("sub")]["all_break"] = True
                    fileData = (await crud.get_last_upload_files(user_id=payload.get("sub"), session=session))
                    await crud.add_final_file_to_table(user_id=payload.get("sub"), session=session, filter_id_global=user_data[payload.get("sub")]["filter_id"])
                    await crud.saving_to_table_data(
                        user_id=payload.get("sub"), session=session, data=ud["excel_result"][ud["skip"]:], file_id=fileData.id
                    )
                    await crud.set_parsing(session=session, status=False, user_id=payload.get("sub"))
                    print("сохранили данные") 
                    user_data[payload.get("sub")]["threads"] = [None] * count_of_threadings
                    user_data[payload.get("sub")]['ban_list'] = []
                    user_data[payload.get("sub")]['status'] = "PARSER_NOT_STARTED_DATA_SAVED"
                    print(user_data[payload.get("sub")]['status'])
                    # user_data[payload.get("sub")]['flag'] = True
                    user_data[payload.get("sub")]['excel_result'] = []
                    del user_data[payload.get("sub")]['brands']
                    user_data[payload.get("sub")]['counter_parsered'] = 0
                    ud["skip"] = 0
                    ud["start"] = 0
                except Exception as e:
                    print('-='*20)
                    print(e)
            if ud["status"] == "Парсер не запущен":
                print("и тут я был")
                if "brands" in ud:
                    if int(ud["counter_parsered"] / ud["count_brands"] * 100) >= 100:
                        ud["status"] = "PARSING_COMPLETED"
                    if len(ud["brands"]) != 0:
                        print(ud["brands"])
                        cnt = len(ud["brands"]) if len(ud["brands"]) < count_of_threadings else count_of_threadings
                        ud["status"] = "PARSER_RUNNING"
                        for index in range(cnt):
                            stmt = select(ProxyBrightData).where(ProxyBrightData.id.in_(user_data[payload.get("sub")]["proxies_id"]))
                            result = await session.execute(stmt)
                            result = result.scalars().all()

                            proxies = [
                                f"http://{i.login}:{i.password}@{i.address}:{i.port}"
                                for i in result]

                            user_data[payload.get("sub")]["events"][index].clear()
                            user_data[payload.get("sub")]["threads"][index] = Thread(
                                target=run, args=(payload.get("sub"), user_data[payload.get("sub")]["using_proxy"], index, proxies)
                            )
                            user_data[payload.get("sub")]["threads"][index].start()
                if "stop" in ud:
                    for stop in user_data[payload.get("sub")]["stop"]:
                        if stop:
                            ud["status"] = "Парсер не запущен"
                            user_data[payload.get("sub")]["all_break"] = True
                            user_data[payload.get("sub")]['ban_list'] = []
                            user_data[payload.get("sub")]['excel_result'] = []
                            user_data[payload.get("sub")]['counter_parsered'] = 0
                            ud["brands"] = []

            await asyncio.sleep(3)
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as e:
        print("-="*20)
        print("sfdlkksfdklsdf")
        print(e)


@router.get("/start/{filter_id}")
async def start(
    filter_id: int,
    proxies_id: str = [6, 7, 8],
    using_proxy: str = "MANGO",
    payload = Depends(get_payload),
    session: AsyncSession = Depends(db_helper.session_depends),
):
    global user_data
    

    await create_empty_json(os.path.join(settings.upload.path_for_upload, f"{payload.get('sub')}_parsing.json"))
    messages = []
    user_id = payload.get("sub")
    filter = await crud.get_filter(
        session=session, user_id=payload.get("sub"), filter_id=filter_id
    )
    try:
        files = (
            await crud.get_last_upload_files(user_id=user_id, session=session)
        )
        files_id = files.id
        files = files.before_parsing_filename
    except Exception as e:
        print("-="*20)
        print(e)
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Файл уже был спаршен"
        )

    if all( [user_data[user_id]["threads"][i] is None or not user_data[user_id]["threads"][i].is_alive() for i in range(count_of_threadings)] ):
        user_data[payload.get("sub")] = {
            "threads": threads.copy(),
            "events": [Event() for _ in range(count_of_threadings)],
            "filter": filter,
            "excel_result": [],
            "status": "PARSER_RUNNING",
            "ban_list": [],
            "count_brands": 1,
            "filter_id": filter_id,
            "flag": False,
            "count_of_threadings": count_of_threadings,
            "stop": [False] * count_of_threadings,
            'counter_parsered': 0,
            "using_proxy": using_proxy,
            "start": 0,
            "skip": 0,
            "proxies_id": proxies_id
        }
    if files is None:
        user_data[payload.get("sub")]["status"] = "Данный файл уже спаршен либо не загружен"
        return JSONResponse("Данный файл уже спаршен")
    elif filter is None:
        user_data[payload.get("sub")]["status"] = "Неизвестный фальтр"
        return JSONResponse("Неизвестный фальтр")
    else:
        await crud.set_parsing(session=session, status=True, user_id=payload.get("sub"))
        await crud.set_filter_for_parsing_file(session=session, filter_id=filter_id, file_id=files_id)
        
        df = pd.read_excel(str(settings.upload.path_for_upload) + "/" + files)

        df = df.apply(lambda col: col.astype(object))
        df_to_list = df.values.tolist()
        brands= create(df_to_list)
        user_data[user_id]["count_brands"] = len(brands)
        user_data[user_id]["brands"] = brands

        for index in range(count_of_threadings):
            stmt = select(ProxyBrightData).where(ProxyBrightData.id.in_(proxies_id))
            result = await session.execute(stmt)
            result = result.scalars().all()

            proxies = [
                f"http://{i.login}:{i.password}@{i.address}:{i.port}"
            for i in result]

            if (
                user_data[user_id]["threads"][index] is None
                or not user_data[user_id]["threads"][index].is_alive()
            ):
                user_data[user_id]["events"][index].clear()
                user_data[user_id]["threads"][index] = Thread(
                    target=run, args=(user_id, using_proxy, index, proxies)
                )
                user_data[user_id]["threads"][index].start()
                messages.append(f"поток {index+1} запущен")
            else:
                messages.append(f"поток {index+1} уже запущен")

        return JSONResponse(messages)


@router.get("/stop")
async def stop(payload = Depends(get_payload), session: AsyncSession = Depends(db_helper.session_depends),):
    global user_data

    user_id = payload.get("sub")
    for index in range(count_of_threadings):
        user_data[user_id]["events"][index].set()
        user_data[user_id]["stop"][index] = True
    await crud.set_parsing(session=session, status=False, user_id=payload.get("sub"))

    return JSONResponse(content="Парсер останавливается")

@router.get("/get_rezerv")
async def get_rezerv(payload = Depends(get_payload)):
    try:
        return FileResponse(os.path.join(settings.upload.path_for_upload, f"{payload.get('sub')}_parsing.json"), media_type='application/json', filename=f"{payload.get('sub')}_parsing.json")
    except:
        return "Нет файла"

@router.get("/get-all-available-country-zone")
async def get_all_available_country_zone(payload = Depends(get_payload)):
    try:
        headers = {
            "Authorization": f"Bearer {settings.proxy.BRIGHT_DATA_TOKEN}",
        }
        r = requests.get("https://api.brightdata.com/countrieslist", headers=headers)
        return {
            "countries": json.loads(r.content)["zone_type"]["DC_shared"]["country_codes"]
        }
    except Exception as e:
        print(e)
        return str(e)

@router.post("/create-new-zones")
async def create_new_zones(countries: ProxyCountriesCreateSchemas, payload = Depends(get_payload),
       session: AsyncSession = Depends(db_helper.session_depends),
    ):
    for country in countries.model_dump()["countries"]:
        headers = {
            "Authorization": f"Bearer {settings.proxy.BRIGHT_DATA_TOKEN}",
        }
        name = f"{country}_zone_{random.randint(10000000, 100000000)}"
        json_data = {
            "zone": {
                "name": name,
                "type": "datacenter"
            },
            "plan": {
                "type": "static",
                "domain_whitelist": "*",
                "ips_type": "shared",
                "bandwidth": "payperusage",
                "ip_alloc_preset": "shared_block",
                "ips": 0,
                "country": f"{country}"
            }
        }

        r = requests.post("https://api.brightdata.com/zone", json=json_data, headers=headers)
        login = f'brd-customer-hl_38726487-zone-{name}'
        password = json.loads(r.content)["zone"]["password"][0]
        address = "brd.superproxy.io"
        port = "33335"

        data = {
            "login": login,
            "password": password,
            "address": address,
            "port": port,
        }

        proxy = ProxyBrightData(**data)
        session.add(proxy)
        await session.commit()

@router.get("/get-all-available-proxies")
async def get_all_available_proxies(
        session: AsyncSession = Depends(db_helper.session_depends),
):
    stmt = select(ProxyBrightData)
    result: Result = await session.execute(stmt)
    return result.scalars().all()