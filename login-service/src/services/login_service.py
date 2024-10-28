import os
from fastapi.security import OAuth2PasswordRequestForm
from httpx import HTTPStatusError, AsyncClient
from pytz import timezone
from tortoise.exceptions import DoesNotExist
from src.models.user_model import User
from src.models.token_models import Token
from passlib.context import CryptContext
from src.utils.exceptions import InvalidCredentialsException, UserBannedException
from datetime import datetime, timezone


class LoginService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.AUTH_SERVICE_URL = os.getenv(
            "AUTH_SERVICE_URL", "http://auth-service:8000/tokens")

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm):
        try:
            user = await User.get(username=form_data.username)

        except DoesNotExist as e:
            raise e

        if not self.pwd_context.verify(form_data.password, user.password):
            raise InvalidCredentialsException(
                "Incorrect username or password")

        if user.account_status == "banned":
            raise UserBannedException("User is banned")

        user.last_login_date = datetime.now(timezone.utc)
        await user.save()

        return user

    async def get_user_token(self, user: User) -> Token:
        user_id = str(user.user_id)
        username = user.username
        try:
            async with AsyncClient() as client:
                response = await client.post(self.AUTH_SERVICE_URL, json={"user_id": user_id, "username": username})
                response.raise_for_status()
                return response.json()

        except HTTPStatusError as e:
            raise e

    async def __fetch_token(self, user_id: str, username: str) -> Token:

        # async def get_user_token(self, form_data: OAuth2PasswordRequestForm):
        #     async with httpx.AsyncClient() as client:
        #         response = await client.post("http://auth-service:8000/tokens", json={"username": form_data.username})
        #         if response.status_code != 200:
        #             raise HTTPException(
        #                 status_code=response.status_code, detail=response.json().get("detail"))
        #         return Token(**response.json())
