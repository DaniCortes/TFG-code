import os

from httpx import AsyncClient, HTTPStatusError
from pymongo import AsyncMongoClient

from src.models.user_model import User
from src.utils.logger import logger


class FollowService:
    def __init__(self):
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.USER_SERVICE_URL = os.getenv(
            "USER_SERVICE_URL", "http://user-service:8000")
        self.mongo_client = AsyncMongoClient(self.MONGO_URL)
        self.database = self.mongo_client.stream_db
        self.collection = self.database.get_collection("follows")

    async def follow_user(self, user_id: str, following_id: str):
        if user_id == following_id:
            raise ValueError("You cannot follow yourself.")

        result = await self.collection.update_one({"user_id": user_id},
                                                  {"$addToSet": {"follows": following_id}}, upsert=True)

        if result.modified_count or result.did_upsert:
            await self.__communicate_with_user_service(
                user_id=following_id, action="follow_user")

    async def unfollow_user(self, user_id: str, unfollowing_id: str):
        if user_id == unfollowing_id:
            raise ValueError("You cannot unfollow yourself.")

        result = await self.collection.update_one({"user_id": user_id},
                                                  {"$pull": {"follows": unfollowing_id}})
        if result.modified_count:
            await self.__communicate_with_user_service(
                user_id=unfollowing_id, action="unfollow_user")

    async def get_follows(self, user_id: str) -> list[User]:
        result = await self.collection.find_one({"user_id": user_id})
        if result:
            if "follows" in result and len(result["follows"]) > 0:
                logger.debug(f"User {user_id} follows: {result['follows']}")
                follows_info = await self.__communicate_with_user_service(
                    user_list=result["follows"], action="get_follows")

                user_list = [User(**user) for user in follows_info]
                return user_list
        return []

    async def __communicate_with_user_service(self, action: str, user_id: str = None, user_list: list = None) -> list[dict] | None:
        async with AsyncClient() as client:
            try:
                if user_list and not user_id and action == "get_follows":
                    response = await client.post(
                        f"{self.USER_SERVICE_URL}/users/bulk",
                        json={"users": user_list}
                    )
                    response.raise_for_status()
                    return response.json()

                elif not user_list and user_id:
                    if action == "follow_user":
                        response = await client.patch(
                            f"{self.USER_SERVICE_URL}/user/{user_id}/followers/inc",
                            json={"user_id": user_id}
                        )
                        response.raise_for_status()

                    elif action == "unfollow_user":
                        response = await client.patch(
                            f"{self.USER_SERVICE_URL}/user/{user_id}/followers/decr",
                            json={"user_id": user_id}
                        )
                        response.raise_for_status()

            except HTTPStatusError as e:
                raise ValueError(
                    f"Failed to notify user service: {e.response.text}")
