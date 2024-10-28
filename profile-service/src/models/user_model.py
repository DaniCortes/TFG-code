from tortoise.models import Model
from tortoise import fields


class User(Model):
    user_id = fields.UUIDField(pk=True)
    username = fields.CharField(max_length=255)
    biography = fields.TextField(null=True)
    profile_picture = fields.TextField(default='default_profile_picture.jpg')
    stream_key = fields.CharField(max_length=255, unique=True, null=True)
    is_admin = fields.BooleanField(default=False)

    class Meta:
        table = "users"
