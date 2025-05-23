import os
from datetime import datetime, timezone
from typing import List

import httpx
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import AsyncMongoClient
from redis import asyncio as aioredis

from src.models.stream_models import (Stream, TransmuxerRequest,
                                      TransmuxerResponse)
from src.models.user_model import User
from src.utils.exceptions import (StreamNotFoundException, TranscoderException,
                                  TransmuxerException,
                                  UserAlreadyStreamingException)
from src.utils.logger import logger


class StreamService:
    def __init__(self):
        self.TRANSMUXING_SERVICE_URL = os.getenv(
            "TRANSMUXING_SERVICE_URL", "http://transmuxing-service:8000")
        self.TRANSCODING_SERVICE_URL = os.getenv(
            "TRANSCODING_SERVICE_URL", "http://transcoding-service:8000")
        self.USER_SERVICE_URL = os.getenv(
            "USER_SERVICE_URL", "http://user-service:8000")
        self.RECORDING_BASE_PATH = os.getenv("RECORDING_BASE_PATH")
        self.HLS_BASE_PATH = os.getenv("HLS_BASE_PATH")
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
        self.mongo_client = AsyncMongoClient(self.MONGO_URL)
        self.database = self.mongo_client.get_database("stream_db")
        self.collection = self.database.get_collection("streams")

        self.redis = aioredis.Redis(
            host="redis", port=6379, db=0, decode_responses=True)

    async def create_stream(self, user: User) -> Stream:
        stream_data = Stream(
            user_id=str(user.user_id),
            status="live"
        )

        if await self.collection.find_one({"user_id": str(user.user_id), "status": "live"}):
            raise UserAlreadyStreamingException(user.username)

        result = await self.collection.insert_one(stream_data.model_dump())

        stream_data.id = str(result.inserted_id)

        transmuxer_request = TransmuxerRequest(
            stream_id=stream_data.id,
            stream_key=user.stream_key
        )

        try:
            await self.__notify_transmuxer(transmuxer_request)

        except TransmuxerException:
            await self.update_stream_status(stream_data.id, "transmux-error")
            raise

        await self._save_stream_id_redis(user)
        await self.__notify_streamer_status(user.stream_key, "live")

        return stream_data

    async def __notify_transmuxer(self, request: TransmuxerRequest, method: str = "post") -> TransmuxerResponse:
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"Connecting to transmuxer: {request.stream_id}")

                response = await client.request(method, f"{self.TRANSMUXING_SERVICE_URL}/streams", json=request.model_dump(mode='json'), timeout=20)

                response.raise_for_status()
                return TransmuxerResponse(**response.json())

        except httpx.HTTPStatusError as e:
            raise TransmuxerException(request.stream_id, str(e))

    async def transcode_stream(self, stream_id: str) -> Stream | None:
        stream = await self.collection.find_one({"_id": ObjectId(stream_id), "status": "finished_transmuxing"})

        if not stream:
            raise StreamNotFoundException(stream_id)

        await self.update_stream_status(stream_id, "to_be_transcoded")

        try:
            logger.info(f"Starting transcoding for stream_id: {stream_id}")
            await self.__notify_transcoder(stream_id)

        except TranscoderException:
            await self.update_stream_status(stream_id, "error_transcoder_connection")
            raise

    async def __notify_transcoder(self, stream_id: str) -> None:
        try:
            async with httpx.AsyncClient() as client:
                logger.debug(f"Connecting to transcoder: {stream_id}")
                response = await client.post(f"{self.TRANSCODING_SERVICE_URL}/streams", json={"stream_id": stream_id})
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise TranscoderException(stream_id, str(e))

    async def __set_end_time_stream(self, stream_id: str) -> bool:
        end_time = datetime.now(timezone.utc)

        try:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(stream_id)},
                {"$set": {"end_time": end_time}}
            )
        except InvalidId as e:
            raise e

        return bool(update_result.modified_count)

    async def get_stream(self, stream_id: str) -> Stream | None:
        try:
            stream_data = await self.collection.find_one({"_id": ObjectId(stream_id)})
        except InvalidId as e:
            raise e

        if stream_data:
            stream_data["id"] = str(stream_data["_id"])
            stream_data["user_id"] = str(stream_data["user_id"])
            del stream_data["_id"]
            return Stream(**stream_data)

        return None

    async def get_live_stream(self, user_id: str) -> Stream | None:
        stream_data = await self.collection.find_one({"user_id": user_id, "status": "live"})

        if stream_data:
            stream_data["id"] = str(stream_data["_id"])
            stream_data["user_id"] = str(stream_data["user_id"])
            del stream_data["_id"]
            return Stream(**stream_data)

        return None

    async def get_live_stream_id(self, user_id: str) -> str | None:
        stream = await self.collection.find_one({"user_id": str(user_id), "status": "live"})
        if not stream:
            return None

        return str(stream["_id"])

    async def stop_stream(self, request: TransmuxerRequest) -> TransmuxerResponse:
        await self.__set_end_time_stream(request.stream_id)
        result = await self.__notify_transmuxer(request, method="delete")
        if result.status != "finished_transmuxing":
            raise TransmuxerException(
                request.stream_id, "Failed to stop stream")

        await self.__notify_streamer_status(request.stream_key, "offline")

    async def update_stream_status(self, stream_id: str, status: str) -> Stream | None:
        try:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(stream_id)},
                {"$set": {"status": status}}
            )
        except InvalidId as e:
            raise e

        if update_result.modified_count == 1:
            return await self.get_stream(stream_id)

        return None

    async def update_stream_tags(self, stream_id: str, tags: list[str]) -> Stream | None:
        try:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(stream_id)},
                {"$addToSet": {"tags": {"$each": tags}}}
            )
        except InvalidId as e:
            raise e

        if update_result.modified_count == 1:
            return await self.get_stream(stream_id)

        return None

    async def update_stream_title(self, stream_id: str, title: str) -> Stream | None:
        try:
            update_result = await self.collection.update_one(
                {"_id": ObjectId(stream_id)},
                {"$set": {"title": title}}
            )
        except InvalidId as e:
            raise e

        if update_result.modified_count == 1:
            return await self.get_stream(stream_id)

        return None

    async def delete_stream(self, stream_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(stream_id)})
        except InvalidId as e:
            raise e

        return bool(result.deleted_count)

    async def list_streams(self, status: str = None) -> List[Stream]:
        streams = []

        if status:
            async for stream_data in self.collection.find({"status": status}):
                stream_data["id"] = str(stream_data["_id"])
                stream_data["user_id"] = str(stream_data["user_id"])
                del stream_data["_id"]
                streams.append(Stream(**stream_data))
        else:
            async for stream_data in self.collection.find():
                stream_data["id"] = str(stream_data["_id"])
                stream_data["user_id"] = str(stream_data["user_id"])
                del stream_data["_id"]
                streams.append(Stream(**stream_data))

        return streams

    async def is_stream_owner(self, user_id: str, stream_id: str) -> bool:
        stream = await self.collection.find_one({"_id": ObjectId(stream_id)})
        return stream["user_id"] == user_id

    async def can_modify_stream(self, user: User, stream_id: str) -> bool:
        if user.is_admin:
            return True

        return await self.is_stream_owner(user.user_id, stream_id)

    async def search_streams(self, q: str, content_range: str) -> tuple[List[Stream], int]:
        if not q:
            return [], 0
        streams = []
        async for stream in self.collection.find({"$title": {"$search": q}}).skip(content_range["start"]).limit(content_range["limit"]):
            stream["id"] = str(stream["_id"])
            stream["user_id"] = str(stream["user_id"])
            del stream["_id"]

            streams.append(Stream(**stream))

        return streams, await self.__get_search_total(q)

    async def __get_search_total(self, q: str) -> int:
        if not q:
            return 0
        return await self.collection.count_documents({"$title": {"$search": q}})

    async def _get_user(self, stream_key: str) -> User | None:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.USER_SERVICE_URL}/user/stream_key/{stream_key}")

            response.raise_for_status()
            user_data = response.json()

            return User(user_id=user_data['user_id'], stream_key=user_data['stream_key'], account_status=user_data['account_status'])

    async def _save_stream_id_redis(self, stream_key: str, stream_id: str):
        await self.redis.set(stream_key, stream_id)

    async def _getdel_stream_id_redis(self, stream_key: str) -> str:
        try:
            return await self.redis.getdel(stream_key)
        except Exception as e:
            logger.error(f"Error fetching stream ID from Redis: {str(e)}")
        return None

    async def __notify_streamer_status(self, stream_key: str, status: str):
        async with httpx.AsyncClient() as client:
            response = await client.patch(f"{self.USER_SERVICE_URL}/user/stream_status", json={"stream_key": stream_key, "stream_status": status})

            response.raise_for_status()

            logger.debug(response.json())
