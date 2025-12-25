import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from connection import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await manager.connect(room_id, ws)
    try:
        while True:
            data = await ws.receive_text()
            manager.last_seen[ws] = asyncio.get_event_loop().time()
            await manager.broadcast(room_id, data, ws)
    except WebSocketDisconnect:
        manager.disconnect(room_id, ws)

@app.on_event("startup")
async def cleanup_task():
    async def loop():
        while True:
            manager.heartbeat()
            await asyncio.sleep(10)
    asyncio.create_task(loop())
