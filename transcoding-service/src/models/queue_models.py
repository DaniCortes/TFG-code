from pydantic import BaseModel


class QueueStatus(BaseModel):
    size: int
    currently_transcoding: str | None
