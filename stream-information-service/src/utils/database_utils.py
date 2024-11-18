from src.models.user_model import UserDB


async def get_user_by_stream_key(stream_key: str):
    return await UserDB.filter(stream_key=stream_key).first()
