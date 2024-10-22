# coding=utf-8

from bson import ObjectId
from fastapi import WebSocket, WebSocketDisconnect
from src.models.user_model import User
from src.services.chat_service import ChatService


class ChatController:
    def __init__(self):
        self.service = ChatService()
        self.mongo_queries = self.service.mongo_queries

    async def handle_connection(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()

        if not await self.streams_collection.find_one({"_id": ObjectId(chat_id)}):
            await websocket.close(code=1008)

        user = await self.service.authenticate_websocket(websocket)

        if not user:
            await websocket.close(code=3000)

        user_id = str(user["user_id"])
        username = user["username"]

        await self.service.connect(websocket, chat_id, user_id)
        if await self.service.is_user_banned(user_id, chat_id):
            await self.service.send_server_message(message="You are restringed from sending messages in this chat", room=chat_id, username=username)
        try:
            while True:
                data = await websocket.receive_text()
                await self.service.broadcast(data, chat_id, username, user_id)

        except WebSocketDisconnect:
            self.handle_disconnect(websocket, chat_id, user_id)

    async def handle_disconnect(self, websocket: WebSocket, room: str, user_id: str):
        self.service.disconnect(websocket, room, user_id)

    async def mute_user(self, current_user: User, muted_user_id: str):
        current_user_id = str(current_user.user_id)

        await self.service.add_to_mute_list(current_user_id, muted_user_id)

        return {"message": "User has been muted"}

    async def ban_user(self, current_user: User, banned_user_id: str):
        current_user_id = str(current_user.user_id)

        await self.service.add_to_ban_list(current_user_id, banned_user_id)

        return {"message": "User has been banned"}

    async def unmute_user(self, current_user: User, unmuted_user_id: str):
        current_user_id = str(current_user.user_id)

        await self.service.remove_from_mute_list(current_user_id, unmuted_user_id)

        return {"message": "User has been unmuted"}

    async def unban_user(self, current_user: User, unbanned_user_id: str):
        current_user_id = str(current_user.user_id)

        await self.service.unban_user(current_user_id, unbanned_user_id)

        return {"message": "User has been unbanned"}
