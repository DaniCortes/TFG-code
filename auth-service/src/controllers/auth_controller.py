from fastapi import HTTPException
import jwt
from src.services.auth_service import AuthService
from src.models.token_models import Token


class AuthController:
    def __init__(self):
        self.auth_service = AuthService()

    async def create_token(self, user_id: str, username: str):
        access_token = self.auth_service.create_access_token(user_id, username)
        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user(self, token: str):
        try:
            username = self.auth_service.get_current_user(token)
            return username

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired",
                                headers={"WWW-Authenticate": "Bearer"})
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token",
                                headers={"WWW-Authenticate": "Bearer"})
