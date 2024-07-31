from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

from app.core.config import settings

import os
import time
from threading import Thread, Event, current_thread


router = APIRouter(prefix="/test", tags=["ТЕСТ НЕ ТРОГАТЬ!!"])

stop_events = [Event(), Event(), Event()]
counters = [0, 0, 0]

def counter_thread(index):
    while not stop_events[index].is_set():
        counters[index] += 1
        print(f"Counter {index+1}: {counters[index]}")
        time.sleep(1)

threads = [None, None, None]

@router.get("/start")
def start_counters():
    messages = []
    for index in range(3):
        if threads[index] is None or not threads[index].is_alive():
            stop_events[index].clear()
            threads[index] = Thread(target=counter_thread, args=(index,))
            threads[index].start()
            messages.append(f"Counter {index+1} started")
        else:
            messages.append(f"Counter {index+1} is already running")
    return {"messages": messages}

@router.get("/stop")
def stop_counters():
    for index in range(3):
        stop_events[index].set()
    return {"message": "All counters stopped"}

@router.get("/status")
def get_status():
    return {
        "counters": [
            {"id": 1, "value": counters[0], "running": not stop_events[0].is_set()},
            {"id": 2, "value": counters[1], "running": not stop_events[1].is_set()},
            {"id": 3, "value": counters[2], "running": not stop_events[2].is_set()}
        ]
    }

templates = Jinja2Templates(directory="app/templates")
files = ''

class ConnectionManager:
    def __init__(self):
        self.active_connection: list[WebSocket] = []

    async def activate(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connection.remove(websocket)

    async def show_message(self, data: str):
        for conn in self.active_connection:
            await conn.send_text(data)

manager = ConnectionManager()

def get_unique_filename(directory, filename: str):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    while os.path.exists(os.path.join(directory, unique_name)):
        unique_name = f"{base}_{counter}{extension}"
        counter += 1

    return unique_name

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse(
        request=request, name="websocket.html"
    )

@router.websocket("/ws/{id}")
async def websocket_endpoint(id: int, websocket: WebSocket):
    await manager.show_message(f"{id} присоединился к чату")
    await manager.activate(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await manager.show_message(f"{id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.show_message(f"{id} покинул чат")