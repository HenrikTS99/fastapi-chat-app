from fastapi import FastAPI
import datetime
from pydantic import BaseModel

app = FastAPI()


chat_log = []


class Message(BaseModel):
    user: str
    message: str
    timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)


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
