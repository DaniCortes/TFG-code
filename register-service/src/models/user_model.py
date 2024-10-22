from tortoise.models import Model
from tortoise import fields


class User(Model):
    username = fields.CharField(max_length=255, pk=True)
    password = fields.CharField(max_length=255)
    stream_key = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = "users"
