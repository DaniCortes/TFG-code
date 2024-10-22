from pydantic import BaseModel, Field
from datetime import datetime, timezone


class Stream(BaseModel):
    id: str | None
    stream_key: str | None
    user_id: str
    status: str
    start_time: datetime = Field(
        default=datetime.now(timezone.utc))
    end_time: datetime | None

    class Config:
        extra = "ignore"


class IngestRequest(BaseModel):
    name: str
    call: str


class TransmuxerRequest(BaseModel):
    stream_id: str
    stream_key: str

    class Config:
        extra = "ignore"


class TransmuxerResponse(BaseModel):
    stream_id: str
    status: str
