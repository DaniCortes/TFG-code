from uuid import UUID

from pydantic import BaseModel, Field, model_serializer
from tortoise import Model, fields
from tortoise.models import Self


class UserDB(Model):
    user_id = fields.UUIDField(pk=True)
    username = fields.TextField(null=False)
    password = fields.TextField(null=False)
    biography = fields.TextField(null=True)
    profile_picture = fields.TextField(default='default_profile_picture.jpg')
    followers_count = fields.IntField(null=False, default=0)
    last_login_date = fields.DatetimeField(null=True)
    account_status = fields.TextField(null=False, default='active')
    stream_status = fields.TextField(null=False, default='offline')
    stream_key = fields.CharField(max_length=255, unique=True, null=False)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"

    @classmethod
    async def get_id(cls, username: str) -> str | None:
        user = await cls.filter(username=username).first()
        if user:
            return str(user.user_id)
        return None

    @classmethod
    async def get_user(cls, stream_key: str) -> Self | None:
        user = await cls.filter(stream_key=stream_key).first()
        return user


class User(BaseModel):
    user_id: str | UUID
    username: str | None = None
    biography: str | None = None
    profile_picture: str | None = None
    followers_count: int | None = None
    stream_key: str | None = None
    is_admin: bool = Field(default=False)
    access_token: str | None = None

    @model_serializer
    def serialize_model(self) -> dict:

        data = {}

        if self.is_admin:
            data["is_admin"] = True

        data.update({
            "user_id": str(self.user_id),
            "username": self.username,
            "followers_count": self.followers_count,
            "biography": self.biography,
            "profile_picture": self.profile_picture,
        })

        if self.stream_key:
            data["stream_key"] = self.stream_key

        if self.access_token:
            data["access_token"] = self.access_token

        return data


class SearchedUser(BaseModel):
    user_id: str
    username: str
    profile_picture: str
    stream_status: str
    followers_count: int


class UserList(BaseModel):
    users: list[str]
