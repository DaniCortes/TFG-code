from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from src.services.auth_service import AuthService
from src.controllers.auth_controller import AuthController
from src.models.token_models import Token, TokenData

router = APIRouter()

service = AuthService()
controller = AuthController(service)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens")


@router.post("/tokens", status_code=201, response_model=Token)
async def create_token(data: TokenData):
    return controller.create_token(data)


@router.get("/users/me", response_model=TokenData)
async def read_users_me(token: Annotated[str, Depends(oauth2_scheme)]):
    return controller.get_current_user(token)
