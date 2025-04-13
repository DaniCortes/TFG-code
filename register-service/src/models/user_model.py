from tortoise import fields
from tortoise.models import Model


class User(Model):
    username = fields.TextField(null=False)
    password = fields.TextField(null=False)
    stream_key = fields.TextField(null=False)

    class Meta:
        table = "users"
