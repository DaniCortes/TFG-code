# coding=utf-8

from bson import ObjectId
from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from src.models.user_model import User
from src.services.http_service import HttpService
from src.services.ws_service import WebsocketService
from src.utils.logger import logger


class ChatController:
    def __init__(self, ws_service: WebsocketService, http_service: HttpService):
        self.ws_service = ws_service
        self.http_service = http_service
        self.streams_collection = self.http_service.streams_collection

    async def handle_connection(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()

        if chat_id != "debug":
            if not await self.streams_collection.find_one({"_id": ObjectId(chat_id)}):
                await websocket.close(code=1008)
                return

        logger.debug("Awaiting for user authentication")
        user = await self.ws_service.authenticate_websocket(websocket)

        if user is None:
            logger.debug("User is not authenticated")
            await websocket.close(code=3000)
            return

        user_id = user.user_id
        username = user.username

        is_user_banned = await self.http_service.is_user_banned(user_id, chat_id, is_room=True)

        self.ws_service.connect(websocket, chat_id, user_id)

        await self.ws_service.send_server_message(event="server_message", room=chat_id, details=f"You have joined the chat.", user_id=user_id)

        if is_user_banned:
            await self.ws_service.send_server_message(event="server_message", room=chat_id, details="You are restricted from sending messages in this chat", user_id=user_id)

        try:
            while True:
                content = await websocket.receive_text()

                is_user_banned = await self.http_service.is_user_banned(user_id, chat_id, is_room=True)

                if not is_user_banned:
                    message_id = await self.http_service.save_message(user_id, username, chat_id, content)

                    await self.ws_service.broadcast(message_id, content, chat_id, username, user_id)

                elif content.strip():
                    await self.ws_service.send_server_message(event="server_message", room=chat_id, details="Your message was not sent as you are currently restricted from sending messages in this chat", user_id=user_id)

                    logger.debug(
                        f"User {user_id} attempted to send a message while restricted in chat {chat_id}")

        except WebSocketDisconnect:
            await self.handle_disconnect(websocket, chat_id, user_id)

    async def handle_disconnect(self, websocket: WebSocket, room: str, user_id: str):
        await self.ws_service.disconnect(websocket, room, user_id)

    async def get_chat_viewers_count(self, chat_id: str):
        if chat_id == "debug":
            return 0

        count = await self.ws_service.get_chat_viewers_count(chat_id)
        return count

    async def mute_user(self, muted_user_id: str, current_user: User):
        current_user_id = str(current_user.user_id)

        result = await self.http_service.mute_user(muted_user_id, current_user_id)

        if not result:
            return {"message": "User is already muted"}

        return {"message": "User has been muted"}

    async def ban_user(self, banned_user_id: str, current_user: User):
        current_user_id = str(current_user.user_id)

        result = await self.http_service.ban_user(banned_user_id, current_user_id)

        if not result:
            return {"message": "User is already banned"}

        return {"message": "User has been banned"}

    async def unmute_user(self, unmuted_user_id: str, current_user: User):
        current_user_id = str(current_user.user_id)

        await self.http_service.unmute_user(unmuted_user_id, current_user_id)

        return {"message": "User has been unmuted"}

    async def unban_user(self, unbanned_user_id: str, current_user: User):
        current_user_id = str(current_user.user_id)

        await self.http_service.unban_user(unbanned_user_id, current_user_id)

        return {"message": "User has been unbanned"}

    async def get_messages(self, chat_id: str):
        messages = await self.http_service.get_messages(chat_id)
        return messages

    async def delete_message(self, chat_id: str, message_id: str, current_user: User):
        if current_user is None:
            return {"message": "User is not authenticated"}

        if await self.http_service._is_owner(chat_id, current_user.user_id) or current_user.is_admin:
            await self.http_service.delete_message(chat_id, message_id)
            await self.ws_service.send_server_message(
                event="delete_message", room=chat_id, details=message_id)
            return  # {"message": "Message has been deleted"}

        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this message"
        )
