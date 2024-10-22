# coding=utf-8

from fastapi import APIRouter, Depends, WebSocket
from src.models.user_model import User
from src.controllers.chat_controller import ChatController
from src.utils.token_utils import get_current_user

router = APIRouter()
chat_controller = ChatController()


@router.websocket("/chat/{chat_id}")
async def chat_endpoint(websocket: WebSocket, chat_id: int):
    await chat_controller.handle_connection(websocket, chat_id)


@router.post("/chat/mute/{muted_user_id}", status_code=201)
async def mute_user(muted_user_id: str, room: str, current_user: User = Depends(get_current_user)):
    return await chat_controller.mute_user(muted_user_id, current_user)


@router.post("/chat/ban/{user_id}", status_code=201)
async def mute_user(banned_user_id: str, user: User = Depends(get_current_user)):
    return await chat_controller.mute_user(banned_user_id, user)
