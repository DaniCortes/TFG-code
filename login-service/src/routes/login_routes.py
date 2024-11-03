from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from src.controllers.login_controller import LoginController
from src.services.login_service import LoginService
from src.models.token_models import Token

router = APIRouter()

service = LoginService()
controller = LoginController(service)


@router.post("/sessions", response_model=Token, status_code=201)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await controller.login(form_data)
