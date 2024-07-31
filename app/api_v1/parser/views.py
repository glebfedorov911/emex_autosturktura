from fastapi import WebSocket, APIRouter, Request, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from threading import Event, Thread

from app.core.config import settings
from app.api_v1.users.crud import get_payload

import time
import asyncio


count_threadings = 10
threads: list[Thread] = [None] * count_threadings
counters = [0] * count_threadings

user_data = {}
templates = Jinja2Templates(directory=settings.templates.templates_path)
router = APIRouter(prefix="/parser", tags=["Parser"])

def counter_threadings(index, user_id):
    global user_data
    while not user_data[user_id]["events"][index].is_set():
        user_data[user_id]["counters"][index] += 1
        time.sleep(1)

@router.get("/")
async def get(request: Request, response: Response, payload = Depends(get_payload)):
    global user_data
    user_data[payload.get('sub')] = {"counters": counters.copy(), "events": [Event() for _ in range(count_threadings)], "threads": threads.copy()}
    return templates.TemplateResponse(
        request=request, name="test.html"
    )

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, payload = Depends(get_payload)):
    global user_data
    await websocket.accept()
    while True:
        await websocket.send_json({"sum":sum(user_data[payload.get("sub")]["counters"])})
        await asyncio.sleep(1)

@router.get("/start/")
async def start_threadings(payload = Depends(get_payload)):
    global user_data
    messages = []
    for index in range(count_threadings):
        if user_data[payload.get("sub")]["threads"][index] is None or not user_data[payload.get("sub")]["threads"][index].is_alive():
            user_data[payload.get("sub")]["events"][index].clear()
            user_data[payload.get("sub")]["threads"][index] = Thread(target=counter_threadings, args=(index, payload.get("sub")))
            user_data[payload.get("sub")]["threads"][index].start()
            messages.append(f"Счетчик {index+1} cтартовал")
        else:
            messages.append(f"Счетчик {index+1} уже запущен")

    return JSONResponse(content=messages)

@router.get("/stop/")
async def stop_threadings(payload = Depends(get_payload)):
    global user_data
    for index in range(count_threadings):
        user_data[payload.get("sub")]["events"][index].set()

    return JSONResponse(content={"messages": "Потоки остановлены"})

@router.get("/status_check/")
async def status_threadings(payload = Depends(get_payload)):
    global user_data
    print(user_data)
    messages = {
        "counter": []
    }

    messages["counter"] = [{"user_id": payload.get("sub"), "id": index+1, "value": user_data[payload.get("sub")]["counters"][index], "running": not user_data[payload.get("sub")]["events"][index].is_set()} for index in range(count_threadings)]

    return JSONResponse(content=messages)