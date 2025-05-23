import secrets

from src.models.user_models import UserDB


async def generate_stream_key():
    while True:
        stream_key = "stream_" + \
            secrets.token_hex(1) + secrets.token_urlsafe(32)

        if not await UserDB.filter(stream_key=stream_key).exists():
            break

    return stream_key
