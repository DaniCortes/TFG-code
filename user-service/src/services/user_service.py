import os
from datetime import datetime, timezone

from asyncpg import UniqueViolationError
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient, HTTPStatusError
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist, IntegrityError

from src.models.token_model import Token
from src.models.user_models import SearchedUser, User, UserDB
from src.utils.exceptions import (InvalidCredentialsException,
                                  UserBannedException)
from src.utils.form_utils import hash_password, validate_username
from src.utils.stream_key_utils import generate_stream_key


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.AUTH_SERVICE_URL = os.getenv(
            "AUTH_SERVICE_URL", "http://auth-service:8000/tokens")

    async def register_user(self, username: str, password: str) -> User:
        validate_username(username)
        hashed_password = hash_password(password)
        stream_key = await generate_stream_key()
        try:
            user = UserDB(username=username, password=hashed_password,
                          stream_key=stream_key)
            await user.save()
            return user
        except UniqueViolationError as e:
            raise e
        except Exception as e:
            raise e

    async def get_user(self, user_id: str):
        try:
            user_db = await UserDB.get(user_id=user_id)

            user = {
                "user_id": str(user_db.user_id),
                "username": user_db.username,
                "profile_picture": user_db.profile_picture,
            }
            return user
        except DoesNotExist as e:
            raise e
        except Exception as e:
            raise e

    async def get_user_by_stream_key(self, stream_key: str):
        try:
            user_db = await UserDB.get(stream_key=stream_key)

            user = {
                "user_id": str(user_db.user_id),
                "username": user_db.username,
                "stream_key": user_db.stream_key,
                "account_status": user_db.account_status
            }

            return user
        except DoesNotExist as e:
            raise e
        except Exception as e:
            raise e

    async def update_stream_status(self, stream_key: str, stream_status: str):
        user = await UserDB.get(stream_key=stream_key)
        user.stream_status = stream_status

        await user.save()
        return {"message": "Stream status updated successfully"}

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm):
        try:
            user = await UserDB.get(username=form_data.username)

        except DoesNotExist as e:
            raise e

        if not self.pwd_context.verify(form_data.password, user.password):
            raise InvalidCredentialsException

        if user.account_status == "banned":
            raise UserBannedException

        user.last_login_date = datetime.now(timezone.utc)
        await user.save()

        return user

    async def get_user_token(self, user: UserDB) -> Token:
        jwt_payload = {
            "user_id": str(user.user_id),
            "username": user.username,
            "is_admin": user.is_admin
        }

        try:
            async with AsyncClient() as client:
                response = await client.post(self.AUTH_SERVICE_URL, json=jwt_payload, headers={
                    "Content-Type": "application/json"}
                )
                response.raise_for_status()
                return response.json()

        except HTTPStatusError as e:
            raise e

    async def change_password(self, current_user: User, updates: dict):
        current_user: UserDB = await UserDB.get(user_id=current_user.user_id)

        if not self.pwd_context.verify(updates["old_password"], current_user.password):
            raise InvalidCredentialsException("Old password is incorrect")

        if updates["new_password"] != updates["confirm_password"]:
            raise IntegrityError("Passwords do not match")

        hashed_password = hash_password(updates["new_password"])
        current_user.password = hashed_password

        await current_user.save()

    async def update_profile(self, current_user: User, updates: dict) -> UserDB:
        current_user: UserDB = await UserDB.get(user_id=current_user.user_id)
        if current_user.stream_status == "live":
            raise IntegrityError("Cannot change stream key while streaming")

        for field, value in updates.items():
            if value is not None or value != "" or value != False or value:

                if field != "stream_key" and field != "username":
                    setattr(current_user, field, value)

                elif field == "stream_key":
                    stream_key = await generate_stream_key()
                    setattr(current_user, field, stream_key)

                elif field == "username":
                    username_exists = await UserDB.filter(username=value).exists()
                    if username_exists and current_user.username != value:
                        raise IntegrityError("Username already exists")

                    current_user.username = value

        await current_user.save()
        return current_user

    async def search_users(self, q: str, content_range: dict) -> tuple[list[SearchedUser], int]:
        if not q:
            return [], 0

        users = await UserDB.filter(username__icontains=q).all()

        if not users:
            return [], 0

        user_list = []
        for user in users:
            user_dict = SearchedUser(user_id=str(
                user.user_id), username=user.username, profile_picture=user.profile_picture)

            user_list.append(user_dict)

        total_users = len(user_list)
        if content_range["start"] > total_users:
            return [], 0
        if content_range["end"] > total_users:
            content_range["end"] = total_users

        user_list = user_list[content_range["start"]:content_range["end"]]
        return user_list, total_users
