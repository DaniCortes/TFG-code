from tortoise import Model
from tortoise import fields


class User(Model):
    user_id = fields.UUIDField(version=4, pk=True)
    username = fields.CharField(max_length=255)
    stream_key = fields.CharField(max_length=255)
    account_status = fields.CharField(max_length=255)

    class Meta:
        table = "users"
