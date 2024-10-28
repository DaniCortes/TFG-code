from pydantic import BaseModel


class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    biography: str | None = None
    profile_picture: str | None = None
    stream_key: bool | None = None
