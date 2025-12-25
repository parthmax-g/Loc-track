import time
from typing import Dict, Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.last_seen: Dict[WebSocket, float] = {}

    async def connect(self, room: str, ws: WebSocket):
        await ws.accept()
        self.rooms.setdefault(room, set()).add(ws)
        self.last_seen[ws] = time.time()

    def disconnect(self, room: str, ws: WebSocket):
        self.rooms.get(room, set()).discard(ws)
        self.last_seen.pop(ws, None)
        if not self.rooms.get(room):
            self.rooms.pop(room, None)

    async def broadcast(self, room: str, message: str, sender: WebSocket):
        for ws in list(self.rooms.get(room, [])):
            if ws != sender:
                await ws.send_text(message)

    def heartbeat(self, timeout=20):
        now = time.time()
        for ws, ts in list(self.last_seen.items()):
            if now - ts > timeout:
                for room in list(self.rooms):
                    self.rooms[room].discard(ws)
                self.last_seen.pop(ws, None)
