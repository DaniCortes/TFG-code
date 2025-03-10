# coding=utf-8

from datetime import datetime

from pydantic import BaseModel


class Message(BaseModel):
    message_id: str
    user_id: str
    username: str
    stream_id: str
    content: str
    timestamp: datetime
    is_deleted: bool
