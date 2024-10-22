from pydantic import BaseModel, Field
from datetime import datetime, timezone
import subprocess


class StreamResponse(BaseModel):
    id: str
    status: str


class StreamRequest(BaseModel):
    stream_id: str
    stream_key: str

    class Config:
        extra = "ignore"


class StreamInfo(BaseModel):
    id: str
    status: str
    hls_path: str
    recording_path: str
