import re

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from httpx import HTTPStatusError, RequestError
from tortoise.exceptions import DoesNotExist, IntegrityError

from models.profile_update_models import (PasswordUpdateRequest,
                                          ProfileUpdateRequest)
from src.models.user_models import User
from src.services.user_service import UserService
from src.utils.exceptions import (InvalidCredentialsException,
                                  UserBannedException)
from src.utils.token_utils import generate_token


class UserController:
    def __init__(self, user_service: UserService):
        self.service = user_service

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

    async def get_user(self, user_id: str):
        try:
            user = await self.service.get_user(user_id)
            return user

        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_user_by_stream_key(self, stream_key: str) -> dict | None:
        try:
            user = await self.service.get_user_by_stream_key(stream_key)
            return user

        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_stream_status(self, stream_key: str, stream_status: str):
        try:

            return await self.service.update_stream_status(stream_key, stream_status)

        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        except IntegrityError as e:
            raise HTTPException(status_code=409, detail=str(e))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def change_password(self, current_user: User, updates: PasswordUpdateRequest):
        try:
            await self.service.change_password(current_user, updates.model_dump())
            return {"message": "Password changed successfully"}

        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        except InvalidCredentialsException as e:
            raise HTTPException(status_code=401, detail=str(e))

        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update_profile(self, current_user: User, updates: ProfileUpdateRequest):

        update_token = False

        if updates.username is not None and updates.username != current_user.username:
            update_token = True

        try:
            updated_user = await self.service.update_profile(current_user, updates.model_dump(exclude_unset=True))

        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

        except IntegrityError as e:
            raise HTTPException(status_code=409, detail=str(e))

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        if update_token:
            updated_user.access_token = await generate_token(str(updated_user.user_id), updated_user.username, updated_user.is_admin)

        return updated_user

    async def search_users(self, q: str, content_range_str: str):
        match = re.match(r'(\w+)=(\d+)-(\d+)', content_range_str)
        if not match:
            raise HTTPException(
                status_code=400, detail="Invalid Range header: wrong format, expected format: item=start-end")

        if match.group(1) != "users":
            raise HTTPException(
                status_code=400, detail="Invalid Range header: wrong item")
        content_range = {
            "item": match.group(1),
            "start": int(match.group(2)),
            "end": int(match.group(3))
        }

        if content_range["start"] > content_range["end"]:
            raise HTTPException(
                status_code=400, detail="Invalid Range header: start cannot be greater than end")

        users, total_users = await self.service.search_users(q, content_range)

        accept_ranges_header = f"Accept-Ranges: {content_range['item']}"
        content_range_header = f"Content-Range: {content_range['item']} {content_range['start']}-{content_range['end']}/{total_users}"

        headers = [accept_ranges_header, content_range_header]

        return users, headers
