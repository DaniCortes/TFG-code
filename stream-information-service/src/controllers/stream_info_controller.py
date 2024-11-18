from bson.errors import InvalidId
from fastapi.exceptions import HTTPException

from src.models.user_model import User
from src.services.stream_info_service import StreamService
from src.utils.database_utils import get_user_by_stream_key
from src.utils.exceptions import (TransmuxerException,
                                  UserAlreadyStreamingException)
from src.utils.logger import logger


class StreamController:
    def __init__(self, stream_service: StreamService):
        self.service = stream_service

    async def create_stream(self, stream_key: str):
        user = await get_user_by_stream_key(stream_key)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.account_status != "active":
            logger.debug(f"User {user.username} is not active")
            raise HTTPException(
                status_code=403, detail="User account is not active")

        try:
            return await self.service.create_stream(user)

        except UserAlreadyStreamingException as e:
            logger.debug(str(e))
            raise HTTPException(status_code=403, detail=str(e))

        except TransmuxerException as e:
            logger.debug(str(e))
            raise HTTPException(status_code=500, detail=str(e))

    async def get_stream(self, stream_id: str):
        try:
            stream = await self.service.get_stream(stream_id)
            return stream
        except InvalidId:
            raise HTTPException(
                status_code=400, detail=f"Stream ID {stream_id} is invalid")

    async def transcode_stream(self, stream_key: str):
        user = await get_user_by_stream_key(stream_key)
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        return await self.service.transcode_stream(user)

    async def update_stream_status(self, stream_id: str, status: str):
        try:
            result = await self.service.update_stream_status(stream_id, status)
        except InvalidId:
            raise HTTPException(
                status_code=404, detail=f"Stream ID {stream_id} is invalid")

        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")

        return result

    async def update_stream_tags(self, stream_id: str, tags: list[str], current_user: User):
        if not await self.service.can_modify_stream(stream_id, current_user):
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this stream")

        try:
            result = await self.service.update_stream_status(stream_id, tags)
        except InvalidId:
            raise HTTPException(
                status_code=400, detail=f"Stream ID {stream_id} is invalid")

        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")

        return result

    async def list_streams(self):
        return await self.service.list_streams()
