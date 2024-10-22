from src.models.user_model import User
from src.utils.validators import validate_username, hash_password
from asyncpg.exceptions import UniqueViolationError
from src.utils.stream_key_utils import generate_stream_key


class RegisterService:
    async def register_user(self, username: str, password: str) -> User:
        validate_username(username)
        hashed_password = hash_password(password)
        while True:
            stream_key = generate_stream_key()
            if not await User.filter(stream_key=stream_key).exists():
                break
        try:
            user = User(username=username, password=hashed_password,
                        stream_key=stream_key)
            await user.save()
            return user
        except UniqueViolationError as e:
            raise e
        except Exception as e:
            raise e
