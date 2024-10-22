
from datetime import datetime, timezone
import os
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient


class MongoQueries:
    def __init__(self):
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
        self.mongo_client = AsyncIOMotorClient(self.MONGO_URL)
        self.database = self.mongo_client.stream_db
        self.streams_collection = self.database.get_collection("streams")
        self.messages_collection = self.database.get_collection("messages")
        self.bans_collection = self.database.get_collection("bans")
        self.mutes_collection = self.database.get_collection("mutes")

    def get_all(self):
        return self.collection.find()

    async def add_to_ban_list(self, user_id: str, banned_user_id: str):
        await self.bans_collection.update_one(
            {"user_id": user_id},
            {"$push": {"banned_users": banned_user_id}},
            upsert=True
        )

    async def remove_from_ban_list(self, user_id: str, unbanned_user_id: str):
        await self.bans_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"banned_users": unbanned_user_id}}
        )

    async def add_to_mute_list(self, user_id: str, muted_user_id: str):
        await self.mutes_collection.update_one(
            {"user_id": user_id},
            {"$push": {"muted_users": muted_user_id}},
            upsert=True
        )

    async def remove_from_mute_list(self, user_id: str, unmuted_user_id: str):
        await self.mutes_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"muted_users": unmuted_user_id}}
        )

    async def is_user_banned(self, banned_user_id: str, stream_id: str):
        stream_document = await self.streams_collection.find_one({"_id": ObjectId(stream_id)})

        banning_user_id = stream_document["user_id"]

        ban_list = await self.bans_collection.find_one({"user_id": banning_user_id})

        if not ban_list:
            return False

        if banned_user_id in ban_list["banned_users"]:
            return True

        return False

    async def is_user_muted(self, muting_user_id: str, muted_user_id: str):
        muted_list = await self.mutes_collection.find_one({"user_id": muting_user_id})

        if not muted_list:
            return False

        if muted_user_id in muted_list["muted_users"]:
            return True

        return False

    async def save_message(self, user_id: str, stream_id: str, text: str):
        message_data = {
            "user_id": user_id,
            "stream_id": stream_id,
            "text": text,
            "timestamp": datetime.now(timezone.utc),
            "is_deleted": False
        }

        result = await self.messages_collection.insert_one(message_data)
        return str(result.inserted_id)
