from fastapi import HTTPException
from src.services.register_service import RegisterService
from tortoise.exceptions import IntegrityError


class RegisterController:
    def __init__(self, register_service: RegisterService):
        self.service = register_service

    async def register_user(self, username: str, password: str):
        try:
            await self.service.register_user(username, password)
            return {"message": "Your account has been created"}
        except IntegrityError:
            raise HTTPException(
                status_code=409, detail="Another user with the username you chose already exists")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=str(e) if str(e) else "Internal server error")
