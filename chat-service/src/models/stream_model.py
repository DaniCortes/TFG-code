from pydantic import BaseModel


class Stream(BaseModel):
    stream_id: str
    user_id: str
    status: str
