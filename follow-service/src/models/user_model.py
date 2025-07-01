from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    username: str
    profile_picture: str
    stream_status: str
