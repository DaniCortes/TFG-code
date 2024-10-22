import os
from typing import List
from bson import ObjectId
from src.models.stream_models import Stream, TransmuxerRequest, TransmuxerResponse
from src.models.user_models import User
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from src.utils.exceptions import StreamNotFoundException, TranscoderException, TransmuxerException, UserAlreadyStreamingException
from datetime import datetime, timezone


class StreamService:
    def __init__(self):
        self.TRANSMUXING_SERVICE_URL = os.getenv("TRANSMUXING_SERVICE_URL")
        self.TRANSCODING_SERVICE_URL = os.getenv("TRANSCODING_SERVICE_URL")
        self.RECORDING_BASE_PATH = os.getenv("RECORDING_BASE_PATH")
        self.HLS_BASE_PATH = os.getenv("HLS_BASE_PATH")
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
        self.mongo_client = AsyncIOMotorClient(self.MONGO_URL)
        self.database = self.mongo_client.stream_db
        self.collection = self.database.get_collection("streams")

    async def create_stream(self, user: User) -> Stream:
        stream_data = Stream(
            user_id=user.user_id,
            status="live"
        )

        if self.collection.find_one({"user_id": user.user_id, "status": "live"}):
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

        return stream_data

    async def __notify_transmuxer(self, request: TransmuxerRequest) -> TransmuxerResponse:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.TRANSMUXING_SERVICE_URL}/streams", json=request.model_dump(mode='json'))
                response.raise_for_status()
                return TransmuxerResponse(**response.json())

        except httpx.HTTPStatusError as e:
            raise TransmuxerException(request.stream_id, str(e))

    async def transcode_stream(self, user: User) -> Stream | None:
        stream_data = await self.collection.find_one({"user_id": user.user_id, "status": "live"})

        if not stream_data:
            raise StreamNotFoundException

        stream_id = str(stream_data["_id"])

        await self.update_stream_status(stream_id, "to_be_transcoded")

        await self.__set_end_time_stream(stream_id)

        try:
            await self.__notify_transcoder(stream_id)

        except TranscoderException:
            await self.update_stream_status(stream_id, "error_transcoder_connection")
            raise

    async def __notify_transcoder(self, request: str) -> None:
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.TRANSCODING_SERVICE_URL}/streams", json={"stream_id": request})

        except httpx.HTTPStatusError as e:
            raise TranscoderException(request.stream_id, str(e))

    async def __set_end_time_stream(self, stream_id: str) -> Stream | None:
        end_time = datetime.now(timezone.utc)

        update_result = await self.collection.update_one(
            {"_id": ObjectId(stream_id)},
            {"$set": {"end_time": end_time}}
        )

        return bool(update_result.modified_count)

    async def get_stream(self, stream_id: str) -> Stream | None:
        stream_data = await self.collection.find_one({"_id": ObjectId(stream_id)})

        if stream_data:
            stream_data["id"] = str(stream_data["_id"])
            del stream_data["_id"]
            return Stream(**stream_data)

        return None

    async def stop_stream(self, stream_key: str) -> Stream | None:
        stream = await self.collection.find_one({"stream_key": stream_key, "status": "live"})

        if not stream:
            raise StreamNotFoundException

        return await self.update_stream_status(str(stream["_id"]), "to_be_transcoded")

    async def update_stream_status(self, stream_id: str, status: str) -> Stream | None:
        update_result = await self.collection.update_one(
            {"_id": ObjectId(stream_id)},
            {"$set": {"status": status}}
        )

        if update_result.modified_count == 1:
            return await self.get_stream(stream_id)

        return None

    async def list_streams(self) -> List[Stream]:
        streams = []

        async for stream_data in self.collection.find():
            del stream_data["stream_key"]
            streams.append(Stream(**stream_data))

        return streams
