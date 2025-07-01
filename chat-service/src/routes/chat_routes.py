# coding=utf-8

from fastapi import APIRouter, Depends, WebSocket

from src.controllers.chat_controller import ChatController
from src.models.user_model import User
from src.services.http_service import HttpService
from src.services.ws_service import WebsocketService
from src.utils.logger import logger
from src.utils.token_utils import get_current_user

router = APIRouter()
ws_service = WebsocketService()
http_service = HttpService()
controller = ChatController(ws_service, http_service)


@router.websocket("/chat/{chat_id}")
async def chat_endpoint(websocket: WebSocket, chat_id: str):
    logger.debug("Websocket connection established")
    await controller.handle_connection(websocket, chat_id)


@router.get("/chat/{chat_id}/viewers_count")
async def get_chat_viewers_count(chat_id: str):
    count = await controller.get_chat_viewers_count(chat_id)
    return {"viewers_count": count}


@router.post("/chat/mute/{muted_user_id}", status_code=201)
async def mute_user(muted_user_id: str, current_user: User = Depends(get_current_user)):
    return await controller.mute_user(muted_user_id, current_user)


@router.delete("/chat/mute/{unmuted_user_id}", status_code=200)
async def unmute_user(unmuted_user_id: str, current_user: User = Depends(get_current_user)):
    return await controller.unmute_user(unmuted_user_id, current_user)


@router.post("/chat/ban/{banned_user_id}", status_code=200)
async def ban_user(banned_user_id: str, user: User = Depends(get_current_user)):
    return await controller.ban_user(banned_user_id, user)


@router.delete("/chat/ban/{unbanned_user_id}", status_code=201)
async def unban_user(unbanned_user_id: str, user: User = Depends(get_current_user)):
    return await controller.unban_user(unbanned_user_id, user)


@router.get("/chat/{chat_id}/messages")
async def get_messages(chat_id: str):
    messages = await controller.get_messages(chat_id)
    return {"messages": messages}


@router.delete("/chat/{chat_id}/messages/{message_id}", status_code=204)
async def delete_message(chat_id: str, message_id: str, current_user: User = Depends(get_current_user)):
    return await controller.delete_message(chat_id, message_id, current_user)
