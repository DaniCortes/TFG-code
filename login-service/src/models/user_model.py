from tortoise.models import Model
from tortoise import fields


class User(Model):
    user_id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    last_login_date = fields.DatetimeField(null=True)
    account_status = fields.CharField(max_length=255, default='active')

    class Meta:
        table = "users"
