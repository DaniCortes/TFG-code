from datetime import timedelta
from fastapi import HTTPException
import jwt
from src.services.auth_service import AuthService
from src.models.token_models import Token, TokenData


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.service = auth_service

    def create_token(self, data: TokenData):
        access_token = self.service.create_access_token(data)
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, token: str, internal_use: bool = False):
        try:
            user_data = self.service.get_current_user(token, internal_use)
            return user_data

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired",
                                headers={"WWW-Authenticate": "Bearer"})
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token",
                                headers={"WWW-Authenticate": "Bearer"})

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}", headers={
                                "WWW-Authenticate": "Bearer"})
