from pydantic import BaseModel


class StreamResponse(BaseModel):
    stream_id: str
    status: str


class StreamRequest(BaseModel):
    stream_id: str
    priority: bool = False
