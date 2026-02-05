from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import datetime
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
chat_log = []


class Message(BaseModel):
    user: str
    message: str
    timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)


chat_log.append(Message(user="Test", message="Testing"))


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.user_sockets: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str):
        self.active_connections.append(websocket)

        if username not in self.user_sockets:
            self.user_sockets[username] = set()
        self.user_sockets[username].add(websocket)

        # Only broadcast if first connection for this username
        if len(self.user_sockets[username]) == 1:
            await self.broadcast(
                {"user": "System", "message": f"{username} has joined the chat"}
            )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

        # Remove socket from username mapping
        for username, sockets in list(self.user_sockets.items()):
            sockets.discard(websocket)
            if not sockets:
                # Last socket for this user disconnected
                del self.user_sockets[username]
                return username  # return for leave message
        return None

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
def root():
    return {"Hello": "World"}


@app.get("/messages")
def get_messages():
    return chat_log


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    username = "Anonymous"
    try:
        await websocket.accept()
        init_data = await websocket.receive_json()
        username = init_data.get("user", "Anonymous")
        await manager.connect(websocket, username)

        while True:
            data = await websocket.receive_json()
            chat_log.append(data)
            await manager.broadcast(data)
    except WebSocketDisconnect:
        left_username = manager.disconnect(websocket)
        if left_username:
            await manager.broadcast(
                {"user": "System", "message": f"{left_username} has left the chat"}
            )
