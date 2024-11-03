from fastapi import APIRouter, Form
from typing import Annotated
from src.controllers.register_controller import RegisterController
from src.services.register_service import RegisterService

router = APIRouter()

service = RegisterService()
controller = RegisterController(service)


@router.post("/users", status_code=201)
async def register_user(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await controller.register_user(username, password)
