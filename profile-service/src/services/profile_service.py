from src.models.user_model import User
from models.user_model import User
from utils.stream_key_utils import generate_stream_key


class ProfileService:
    async def update_profile(self, current_user: User, updates: dict):
        for field, value in updates.items():
            if value is not None or value != "" or value != False:
                if field != "stream_key" or field != "username":
                    setattr(current_user, field, value)
                elif field == "stream_key":
                    while True:
                        stream_key = generate_stream_key()
                        setattr(current_user, field, stream_key)
                        if not await User.filter(stream_key=stream_key).exists():
                            break
                elif field == "username":
                    if await User.filter(username=value).exists():
                        raise ValueError("Username already exists")
                    current_user.username = value

        await current_user.save()
        return current_user
