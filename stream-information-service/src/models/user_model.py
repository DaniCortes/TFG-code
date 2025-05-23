from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    username: str | None = None
    account_status: str | None = None
    stream_key: str | None = None
    is_admin: bool | None = None
