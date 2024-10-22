from models.user_models import User


async def get_user_by_stream_key(stream_key: str):
    return await User.filter(stream_key=stream_key).first()
