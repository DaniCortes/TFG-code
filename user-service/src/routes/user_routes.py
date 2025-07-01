from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, Response
from fastapi.security import OAuth2PasswordRequestForm

from src.controllers.user_controller import UserController
from src.models.profile_update_models import (PasswordUpdateRequest,
                                              ProfileUpdateRequest,
                                              StreamStatusUpdateRequest)
from src.models.token_model import Token
from src.models.user_models import SearchedUser, User, UserList
from src.services.user_service import UserService
from src.utils.token_utils import get_current_user

router = APIRouter()

service = UserService()
controller = UserController(service)


@router.post("/users", status_code=201)
async def register_user(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await controller.register_user(username, password)


@router.post("/users/bulk", status_code=200, response_model=list[dict])
async def list_users(user_list: UserList):
    return await controller.get_users_info(user_list.users)


@router.get("/user/{user_id}", status_code=200, response_model=User)
async def get_user(user_id: str):
    return await controller.get_user_by_id(user_id)


@router.get("/user/stream_key/{stream_key}", status_code=200)
async def get_user_by_stream_key(stream_key: str):
    return await controller.get_user_by_stream_key(stream_key)


@router.patch("/user/{user_id}/followers/{inc_or_decr}", status_code=200)
async def update_followers(user_id: str, inc_or_decr: str):
    return await controller.update_followers(user_id, inc_or_decr)


@router.patch("/user/stream_status", status_code=200)
async def update_stream_status(stream_status: StreamStatusUpdateRequest):
    return await controller.update_stream_status(stream_status.stream_key, stream_status.stream_status)


@router.get("/users/{username}", status_code=200, response_model=User)
async def get_user(username: str):
    return await controller.get_user_by_username(username)


@router.get("/search/users", response_model=list[SearchedUser], status_code=200)
async def get_users(response: Response, q: str, range: str = Header(...)):
    users, headers = await controller.search_users(q, range)
    for header in headers:
        response.headers[header.split(":")[0]] = header.split(":")[1].strip()

    return users


@router.post("/sessions", response_model=Token, status_code=201)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await controller.login(form_data)


@router.get("/profile", response_model=User, status_code=200)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/profile", response_model=User, status_code=200)
async def update_profile(updates: ProfileUpdateRequest, current_user: User = Depends(get_current_user)):
    return await controller.update_profile(current_user, updates)


@router.patch("/profile/password", status_code=200)
async def update_password(updates: PasswordUpdateRequest, current_user: User = Depends(get_current_user)):
    return await controller.change_password(current_user, updates)
