import os
from datetime import datetime, timedelta, timezone

import jwt

from src.models.token_models import TokenData


class AuthService:
    def __init__(self):
        self.SECRET_KEY = os.getenv("JWT_SECRET")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_DAYS = 14

    def create_access_token(self, data: TokenData):
        user_info = {"sub": data.user_id,
                     "preferred_username": data.username,
                     "is_admin": data.is_admin,
                     "iat": datetime.now(timezone.utc),
                     "exp": datetime.now(timezone.utc) + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)}

        encoded_jwt = jwt.encode(
            user_info, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def get_current_user(self, token: str, internal_use: bool = False):
        decode_options = {
            "require": ["exp", "sub", "preferred_username"],
            "verify_exp": True
        }

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[
                self.ALGORITHM], options=decode_options)
            user_id = str(payload.get("sub"))
            username = str(payload.get("preferred_username"))
            is_admin = bool(payload.get("is_admin")) if payload.get(
                "is_admin") is not None else False
            if internal_use:
                exp = datetime.fromtimestamp(payload.get("exp"))
                return TokenData(user_id=user_id, username=username, is_admin=is_admin, exp=exp)

            return TokenData(user_id=user_id, username=username, is_admin=is_admin)

        except jwt.ExpiredSignatureError as e:
            raise e

        except jwt.InvalidTokenError as e:
            raise e

        except Exception as e:
            raise e
