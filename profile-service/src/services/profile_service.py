from src.models.user_model import UserDB, User
from src.utils.stream_key_utils import generate_stream_key
from tortoise.exceptions import IntegrityError


class ProfileService:
    async def update_profile(self, current_user: User, updates: dict):
        current_user = await UserDB.get(user_id=current_user.user_id)
        for field, value in updates.items():
            if value is not None or value != "" or value != False:
                if field is not "stream_key" and field is not "username":
                    setattr(current_user, field, value)

                elif field is "stream_key":
                    while True:
                        stream_key = generate_stream_key()
                        setattr(current_user, field, stream_key)
                        if not await UserDB.filter(stream_key=stream_key).exists():
                            break

                elif field is "username":
                    username_exists = await UserDB.filter(username=value).exists()
                    if username_exists and current_user.username != value:
                        raise IntegrityError("Username already exists")

                    current_user.username = value

        await current_user.save()
        return current_user
