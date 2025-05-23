import os

from pymongo import AsyncMongoClient


class FollowService:
    def __init__(self):
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.mongo_client = AsyncMongoClient(self.MONGO_URL)
        self.database = self.mongo_client.stream_db
        self.collection = self.database.get_collection("follows")

    async def follow_user(self, user_id: str, following_id: str):
        if user_id == following_id:
            raise ValueError("You cannot follow yourself.")

        result = await self.collection.update_one({"user_id": user_id},
                                                  {"$addToSet": {"following": following_id}}, upsert=True)

        if result.modified_count or result.did_upsert:
            await self.collection.update_one({"user_id": following_id},
                                             {"$inc": {"followers": 1}}, upsert=True)

    async def unfollow_user(self, user_id: str, unfollowing_id: str):
        if user_id == unfollowing_id:
            raise ValueError("You cannot unfollow yourself.")

        result = await self.collection.update_one({"user_id": user_id},
                                                  {"$pull": {"following": unfollowing_id}})
        if result.modified_count:
            await self.collection.update_one({"user_id": unfollowing_id},
                                             {"$inc": {"followers": -1}})

    async def get_followers(self, user_id: str) -> int:
        result = await self.collection.find_one({"user_id": user_id})

        if result:
            if "followers" in result:
                return result["followers"]

        return 0

    async def get_following(self, user_id: str) -> list:
        result = await self.collection.find_one({"user_id": user_id})
        if result:
            if "following" in result:
                return result["following"]

        return []
