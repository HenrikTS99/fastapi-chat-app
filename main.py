from fastapi import FastAPI
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


@app.get("/")
def root():
    return {"Hello": "World"}


@app.post("/message")
def post_message(message: Message):
    chat_log.append(message)
    return message


@app.get("/messages")
def get_messages():
    return chat_log
