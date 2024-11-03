from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.services.login_service import LoginService
from httpx import HTTPStatusError, RequestError
from tortoise.exceptions import DoesNotExist
from src.utils.exceptions import InvalidCredentialsException, UserBannedException


class LoginController:
    def __init__(self, login_service: LoginService):
        self.service = login_service

    async def login(self, form_data: OAuth2PasswordRequestForm):
        try:
            user = await self.service.authenticate_user(form_data)
            return await self.service.get_user_token(user)

        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        except InvalidCredentialsException as e:
            raise HTTPException(status_code=401, detail=str(e))
        except UserBannedException as e:
            raise HTTPException(status_code=403, detail=str(e))
        except HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail="Internal server error")
        except RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))
