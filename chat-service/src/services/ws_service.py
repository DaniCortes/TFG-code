# coding=utf-8

import asyncio
from typing import Dict, Set

from fastapi import WebSocket

from src.utils.logger import logger
from src.utils.validate_user import validate_user


class WebsocketService:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {}

    def connect(self, websocket: WebSocket, room: str, user_id: str):
        if room not in self.active_connections:
            self.active_connections[room] = {}

        if user_id not in self.active_connections[room]:
            self.active_connections[room][user_id] = set()

        self.active_connections[room][user_id].add(websocket)

    async def authenticate_websocket(self, websocket: WebSocket):
        try:
            jwt_token = await asyncio.wait_for(websocket.receive_text(), timeout=5)

        except asyncio.TimeoutError:
            return None

        try:
            user = await validate_user(jwt_token)

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None

        if user.username is None:
            return None

        logger.debug(f"User \"{user.username}\" has been authenticated")

        return user

    async def disconnect(self, websocket: WebSocket, room: str, user_id: str):

        self.active_connections[room][user_id].discard(websocket)

        if not self.active_connections[room][user_id]:
            del self.active_connections[room][user_id]

            if not self.active_connections[room]:
                del self.active_connections[room]

    async def broadcast(self, message_id: str, content: str, room: str, username: str, user_id: str):

        content = content.strip()

        if room in self.active_connections:
            for recipient_id, websockets in self.active_connections[room].items():

                for websocket in websockets:
                    await self.send_user_message(websocket, user_id, username, message_id, content)

    async def send_server_message(self, event: str, room: str, details: str = None, user_id: str = None):

        if event == "delete_message" or event == "broadcast_message":

            if user_id is None and details is not None:
                if room in self.active_connections:
                    for recipient_id, websockets in self.active_connections[room].items():
                        for websocket in websockets:
                            message_data = {
                                "event": event,
                                "content": details
                            }
                            await self.send(websocket, message_data)

        elif event == "server_message":

            if user_id is not None and details is not None:
                if room in self.active_connections and user_id in self.active_connections[room]:
                    for websocket in self.active_connections[room][user_id]:
                        message_data = {
                            "event": event,
                            "content": details
                        }
                        await self.send(websocket, message_data)

        elif event == "ban_user":
            if user_id is not None and details is not None:
                if room in self.active_connections and user_id in self.active_connections[room]:
                    for websocket in self.active_connections[room][user_id]:
                        message_data = {
                            "event": event,
                            "content": details
                        }
                        await self.send(websocket, message_data)

    async def send_user_message(self, websocket: WebSocket, user_id: str, username: str, message_id: str, message: str):
        message_data = {
            "event": "user_message",
            "sender_id": user_id,
            "sender_username": username,
            "message_id": message_id,
            "content": message
        }
        await self.send(websocket, message_data)

    async def send(self, websocket: WebSocket, data: Dict):
        await websocket.send_json(data)
