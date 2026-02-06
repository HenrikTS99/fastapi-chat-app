import datetime
import sqlite3
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Improved Configuration ---
# Get the absolute path to the directory containing this script
SCRIPT_DIR = Path(__file__).parent
# Define the database path relative to the script directory
DATABASE_PATH = SCRIPT_DIR / "chat.db"


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


init_db()


app = FastAPI()

# For production, you should restrict this to your frontend's actual domain
# Example: allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"]
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Message(BaseModel):
    user: str
    message: str
    timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)


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
    return load_messages()


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
            save_message(data["user"], data["message"])
            await manager.broadcast(data)
    except WebSocketDisconnect:
        left_username = manager.disconnect(websocket)
        if left_username:
            await manager.broadcast(
                {"user": "System", "message": f"{left_username} has left the chat"}
            )


def save_message(user, message):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user, message) VALUES(?, ?)", (user, message)
        )
        conn.commit()


def load_messages():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user, message FROM messages ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()

    messages = [{"user": user, "message": message} for user, message in rows]
    return messages[::-1]
