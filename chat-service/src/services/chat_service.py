# coding=utf-8

from uuid import UUID
from fastapi import WebSocket
from typing import Dict, Set
from utils.validate_user import validate_user
from src.utils.mongodb_queries import MongoQueries


class ChatService:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {}
        self.mongo_queries = MongoQueries()

    async def connect(self, websocket: WebSocket, room: str, user_id: str):
        if room not in self.active_connections:
            self.active_connections[room] = {}

        if user_id not in self.active_connections[room]:
            self.active_connections[room][user_id] = set()

        self.active_connections[room][user_id].add(websocket)

    async def authenticate_websocket(self, websocket: WebSocket) -> Dict:
        jwt_token = await websocket.receive_text()

        try:
            user = await validate_user(jwt_token)

        except:
            return None

        if "username" not in user:
            return None

        return user

    async def disconnect(self, websocket: WebSocket, room: str, user_id: str):
        for websocket in self.active_connections[room][user_id]:
            await websocket.close()

        self.active_connections[room][user_id].discard(websocket)

        if not self.active_connections[room][user_id]:
            del self.active_connections[room][user_id]

            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast(self, message: str, room: str, username: str, user_id: str):
        if room in self.active_connections:
            for recipient_id, websockets in self.active_connections[room].items():
                if not await self.mongo_queries.is_user_muted(recipient_id, muted_user_id=user_id):

                    message_id = await self.mongo_queries.save_message(user_id, room, message)

                    for websocket in websockets:
                        await self.send_message(websocket, user_id, username, message_id, message)

    async def send_server_message(self, message: str, room: str, user_id: str):
        if room in self.active_connections and user_id in self.active_connections[room]:
            for websocket in self.active_connections[room][user_id]:
                message_data = {
                    "event": "server_message",
                    "content": message
                }
                await self.send(websocket, message_data)

    async def send_message(self, websocket: WebSocket, user_id: str, username: str, message_id: str, message: str):
        message_data = {
            "event": "message",
            "sender_id": user_id,
            "sender_username": username,
            "message_id": message_id,
            "content": message
        }
        await self.send(websocket, message_data)

    async def send(websocket: WebSocket, data: Dict):
        await websocket.send_json(data)

    async def is_user_banned(self, user_id: str, room: str):
        return await self.mongo_queries.is_user_banned(user_id, room)

    async def mute_user(self, muted_user_id: str, current_user_id: str):
        await self.mongo_queries.add_to_mute_list(current_user_id, muted_user_id)

    async def ban_user(self, banned_user_id: str, current_user_id: str):
        await self.mongo_queries.add_to_ban_list(current_user_id, banned_user_id)

    async def unmute_user(self, user_id: str, unmuted_user_id: str):
        await self.mongo_queries.remove_from_mute_list(user_id, unmuted_user_id)

    async def unban_user(self, user_id: str, unbanned_user_id: str):
        await self.mongo_queries.remove_from_mute_list(user_id, unbanned_user_id)
