from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from threading import Thread, Event

from app.core.config import settings
from app.api_v1.users.crud import get_payload

import asyncio
import time


router = APIRouter(prefix="/new_parser", tags=["New Parser"])
templates = Jinja2Templates(directory=settings.templates.templates_path)

count_of_threadings = 8
threads: list[Thread] = [None] * count_of_threadings
counters: list[int] = [0] * count_of_threadings

user_data = {}

def counter_threadings(index, user_id):
    global user_data
    while not user_data[user_id]["events"][index].is_set():
        user_data[user_id]["counters"][index] += 1
        time.sleep(1)

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="test2.html"
    )

@router.websocket("/ws2")
async def websocket_endpoint(websocket: WebSocket, payload = Depends(get_payload)):
    global user_data

    user_data[payload.get("sub")] = {"threads": threads.copy(), "events": [Event() for _ in range(count_of_threadings)], "counters": counters.copy()}
    await websocket.accept()
    try:
        while True:
            await websocket.send_json({"sum_counters": sum(user_data[payload.get("sub")]["counters"])})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await websocket.close()

@router.get("/start")
async def start(payload=Depends(get_payload)):
    global user_data

    messages = []
    user_id = payload.get("sub")
    for index in range(count_of_threadings):
        if user_data[user_id]["threads"][index] is None or not user_data[user_id]["threads"][index].is_alive():
            user_data[user_id]["events"][index].clear()
            user_data[user_id]["threads"][index] = Thread(target=counter_threadings, args=(index, user_id))
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
    return JSONResponse(content="Потоки остановлены")
    

@router.get("/status")
async def status(payload=Depends(get_payload)):
    global user_data
    
    user_id = payload.get("sub")
    messages = {"counter": []}  
    for index in range(count_of_threadings):
        messages["counter"] = [{"index": index+1, "count": user_data[user_id]["counters"][index], "running": not user_data[user_id]["events"][index].is_set()} for index in range(count_of_threadings)]

    return JSONResponse(content=messages)