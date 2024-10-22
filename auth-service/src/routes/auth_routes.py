from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from src.controllers.auth_controller import AuthController
from src.models.token_models import Token, TokenData

router = APIRouter()
controller = AuthController()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens")


@router.post("/tokens", status_code=201, response_model=Token)
async def create_token(user_id: str, username: str):
    return await controller.create_token(user_id, username)


@router.get("/users/me", response_model=TokenData)
async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
    return await controller.get_current_user(token)
