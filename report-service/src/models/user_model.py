from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    username: str
    is_admin: bool
