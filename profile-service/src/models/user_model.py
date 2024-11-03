from uuid import UUID
from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel, model_serializer, Field


class UserDB(Model):
    user_id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=255)
    biography = fields.TextField(null=True)
    profile_picture = fields.TextField(default='default_profile_picture.jpg')
    stream_key = fields.CharField(max_length=255, unique=True, null=True)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"


class User(BaseModel):
    user_id: str | UUID
    username: str
    biography: str | None = None
    profile_picture: str
    stream_key: str
    is_admin: bool = False
    access_token: str | None = None

    @model_serializer
    def serialize_model(self) -> dict:

        data = {}

        if self.is_admin:
            data["is_admin"] = True
            data["user_id"] = str(self.user_id)

        data.update({
            "username": self.username,
            "biography": self.biography,
            "profile_picture": self.profile_picture,
            "stream_key": self.stream_key,
        })

        if self.access_token:
            data["access_token"] = self.access_token

        return data
