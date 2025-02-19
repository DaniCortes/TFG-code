from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    is_admin: bool = False

    class Config:
        extra = "ignore"
