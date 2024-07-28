from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import asyncio


router = APIRouter(prefix="/websocket", tags=["Websocket"])

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Чат</title>
    </head>
    <body>
        <h1>ВебСокет чат</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" placeholder="Введите сообщение">
            <button>Отправить</button>
        </form>
        <ul id="messages">
        </ul>
        <script>
            let id = Date.now()
            let ws = new WebSocket(`ws://localhost:8000/api/v1/websocket/ws/${id}`)
            ws.onmessage = function(event) {
                let messages = document.querySelector("#messages")
                let message = document.createElement("li")
                let content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            }
            function sendMessage(event) {
                let input = document.querySelector("input")
                ws.send(input.value)
                input.value = ""
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_conn: list[WebSocket] = []

    async def activate(self, websocket: WebSocket):
        await websocket.accept()
        self.active_conn.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_conn.remove(websocket)

    async def broadcast(self, data):
        for conn in self.active_conn:
            await conn.send_text(data)

manager = ConnectionManager()

@router.get("/")
async def get():
    return HTMLResponse(html)

@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: int):
    await manager.activate(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{id}: {data}") 
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{id} покинул чат") 

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     a = 25
#     b = 5
#     while True:
#         c = a // b
#         await websocket.send_json({
#             "a": a,
#             "b": b,
#             "result": c
#         })
#         a += 5
#         await asyncio.sleep(5)