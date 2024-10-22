# coding=utf-8

from pydantic import BaseModel


class StreamResponse(BaseModel):
    id: str
    status: str
