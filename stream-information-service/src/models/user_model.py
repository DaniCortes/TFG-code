from uuid import UUID

from pydantic import BaseModel
from tortoise import Model, fields


class UserDB(Model):
    user_id = fields.UUIDField(version=4, pk=True)
    username = fields.CharField(max_length=255)
    stream_key = fields.CharField(max_length=255)
    account_status = fields.CharField(max_length=255)

    class Meta:
        table = "users"


class User(BaseModel):
    user_id: UUID
    username: str
    account_status: str
    is_admin: bool
