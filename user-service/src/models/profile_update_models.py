from pydantic import BaseModel


class ProfileUpdateRequest(BaseModel):
    username: str | None = None
    biography: str | None = None
    stream_key: bool | None = None


class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str


class StreamStatusUpdateRequest(BaseModel):
    stream_key: str
    stream_status: str
