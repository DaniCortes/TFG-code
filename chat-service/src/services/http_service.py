
import os
from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from pymongo import AsyncMongoClient

from src.models.chat_models import Message


class HttpService:
    def __init__(self):
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
        self.mongo_client = AsyncMongoClient(self.MONGO_URL)
        self.database = self.mongo_client.stream_db
        self.streams_collection = self.database.get_collection("streams")
        self.messages_collection = self.database.get_collection("messages")
        self.bans_collection = self.database.get_collection("bans")
        self.mutes_collection = self.database.get_collection("mutes")

    def get_all(self):
        return self.streams_collection.find()

    async def ban_user(self, banned_user_id: str, user_id: str):
        result = await self.bans_collection.update_one(
            {
                "user_id": user_id
            },
            {
                "$addToSet": {
                    "banned_users": banned_user_id
                },
                "$setOnInsert": {
                    "created_at": datetime.now(timezone.utc)
                },
            },
            upsert=True
        )

        if result.modified_count > 0 or result.did_upsert:
            await self.bans_collection.update_one(
                {
                    "_id": result.upserted_id,
                },
                {
                    "$set": {
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return True

        return False

    async def is_user_banned(self, banned_user_id: str, user_or_room_id: str, is_room=False):
        user_id = user_or_room_id

        if is_room and user_or_room_id != "debug":
            result = await self.streams_collection.find_one(
                {
                    "_id": ObjectId(user_or_room_id),
                },
                {
                    "user_id": 1
                }
            )

            if result:
                user_id = result["user_id"]

        result = await self.bans_collection.find_one(
            {
                "user_id": user_id,
                "banned_users": banned_user_id
            },
            {
                "_id": 1,
            }
        )

        return result is not None

    async def unban_user(self, unbanned_user_id: str, user_id: str):
        result = await self.bans_collection.update_one(
            {
                "user_id": user_id
            },
            {
                "$pull": {"banned_users": unbanned_user_id}
            }
        )

        if result.modified_count > 0 or result.did_upsert:
            await self.bans_collection.update_one(
                {
                    "_id": result.upserted_id,
                },
                {
                    "$set": {
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return True

        return False

    async def get_banned_users(self, user_id: str) -> List[str]:
        result = await self.bans_collection.find_one(
            {
                "user_id": user_id,
            },
            {
                "banned_users": 1
            }
        )

        if result and "banned_users" in result:
            return result["banned_users"]

        return []

    async def mute_user(self, muted_user_id: str, user_id: str):

        result = await self.mutes_collection.update_one(
            {
                "user_id": user_id
            },
            {
                "$addToSet": {"muted_users": muted_user_id},
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )

        if result.modified_count > 0 or result.did_upsert:
            await self.mutes_collection.update_one(
                {
                    "_id": result.upserted_id,
                },
                {
                    "$set": {
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            return True

        return False

    async def is_user_muted(self, muted_user_id: str, user_id: str):
        result = await self.mutes_collection.find_one(
            {
                "user_id": user_id,
                "muted_users": muted_user_id
            },
            {"_id": 1}
        )

        return result is not None

    async def unmute_user(self, unmuted_user_id: str, user_id: str):
        result = await self.mutes_collection.update_one(
            {
                "user_id": user_id
            },
            {
                "$pull": {"muted_users": unmuted_user_id},
            }
        )

        if result.modified_count > 0 or result.did_upsert:
            await self.mutes_collection.update_one(
                {
                    "_id": result.upserted_id
                },
                {
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                }
            )

            return True

        return False

    async def get_muted_users(self, user_id: str) -> List[str]:
        result = await self.mutes_collection.find_one(
            {"user_id": user_id},
            {"muted_users": 1}
        )

        if result and "muted_users" in result:
            return result["muted_users"]

        return []

    async def save_message(self, user_id: str, username: str, stream_id: str, content: str):
        message_data = {
            "user_id": user_id,
            "username": username,
            "stream_id": stream_id,
            "content": content,
            "timestamp": datetime.now(timezone.utc),
            "is_deleted": False
        }

        result = await self.messages_collection.insert_one(message_data)
        return str(result.inserted_id)

    async def get_messages(self, stream_id: str, is_deleted: bool = False):
        if stream_id != "debug":
            stream_timestamp = await self.streams_collection.find_one(
                {
                    "_id": ObjectId(stream_id)
                },
                {
                    "timestamp": 1
                }
            )

        messages_result = await self.messages_collection.find(
            {
                "stream_id": stream_id,
                "is_deleted": is_deleted
            }
        ).to_list()

        messages = []
        for message_result in messages_result:
            message = Message(message_id=str(message_result["_id"]),
                              user_id=message_result["user_id"],
                              username=message_result["username"],
                              stream_id=message_result["stream_id"],
                              content=message_result["content"],
                              timestamp=message_result["timestamp"],
                              is_deleted=message_result["is_deleted"])
            messages.append(message)
        return messages

    async def delete_message(self, stream_id: str, message_id: str):
        await self.messages_collection.update_one(
            {
                "_id": ObjectId(message_id),
                "stream_id": stream_id
            },
            {
                "$set": {
                    "is_deleted": True
                }
            }
        )

    async def _is_owner(self, stream_id: str, user_id: str):
        if stream_id == "debug":
            return True

        result = await self.streams_collection.find_one(
            {
                "_id": ObjectId(stream_id),
                "user_id": user_id
            },
            {
                "_id": 1
            }
        )

        return result is not None
