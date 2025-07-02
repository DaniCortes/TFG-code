from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class Stream(BaseModel):
    id: str | None = None
    user_id: str
    title: str = Field(default="Default title")
    status: str
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime | None = None
    model_config = ConfigDict(extra="ignore")


class IngestRequest(BaseModel):
    name: str
    call: str
    model_config = ConfigDict(extra="ignore")


class TransmuxerRequest(BaseModel):
    stream_id: str
    stream_key: str | None = None

    model_config = ConfigDict(extra="ignore")


class TransmuxerResponse(BaseModel):
    stream_id: str
    status: str


class StatusRequest(BaseModel):
    status: str


class TagsRequest(BaseModel):
    tags: list[str]


class TitleRequest(BaseModel):
    title: str
