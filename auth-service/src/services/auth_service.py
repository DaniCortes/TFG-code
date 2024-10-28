import os
from datetime import datetime, timedelta, timezone
import jwt

from src.models.token_models import TokenData


class AuthService:
    def __init__(self):
        self.SECRET_KEY = os.getenv("JWT_SECRET")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_DAYS = 14

    def create_access_token(self, user_id: str, username: str, is_admin: bool, expires_delta: timedelta | None = None):
        user_info = {"sub": user_id,
                     "preferred_username": username, "is_admin": is_admin}
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(
                timezone.utc) + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)

        user_info.update({"exp": expire})

        encoded_jwt = jwt.encode(
            user_info, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def get_current_user(self, token: str):
        decode_options = {
            "require": ["exp", "sub", "preferred_username"],
            "verify_exp": True
        }

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[
                self.ALGORITHM], options=decode_options)
            user_id = str(payload.get("sub"))
            username = str(payload.get("preferred_username"))

            return TokenData(user_id, username)

        except jwt.ExpiredSignatureError as e:
            raise e

        except jwt.InvalidTokenError as e:
            raise e
