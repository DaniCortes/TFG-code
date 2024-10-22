from fastapi import APIRouter, Form
from typing import Annotated
from src.controllers.register_controller import RegisterController

router = APIRouter()
controller = RegisterController()


@router.post("/users", status_code=201)
async def register_user(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return await controller.register_user(username, password)
