import re

from bson.errors import InvalidId
from fastapi.exceptions import HTTPException

from src.models.stream_models import Stream, TransmuxerRequest
from src.models.user_model import User
from src.services.stream_info_service import StreamService
from src.utils.exceptions import (TransmuxerException,
                                  UserAlreadyStreamingException)
from src.utils.logger import logger


class StreamController:
    def __init__(self, stream_service: StreamService):
        self.service = stream_service

    async def create_stream(self, stream_key: str) -> Stream:
        user = await self.service._get_user(stream_key=stream_key)

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

    async def get_live_stream(self, user_id: str):
        try:
            stream = await self.service.get_live_stream(user_id=user_id)
            if not stream:
                raise HTTPException(
                    status_code=404, detail=f"User {user_id} does not have an active stream.")

            return stream

        except InvalidId:
            raise HTTPException(
                status_code=400, detail=f"Stream ID {user_id} is invalid")

    async def search_streams(self, q: str, content_range_str: str):
        match = re.match(r'(\w+)=(\d+)-(\d+)', content_range_str)
        if not match:
            raise HTTPException(
                status_code=400, detail="Invalid Range header: wrong format, expected format: item=start-end")

        if match.group(1) != "livestreams" and match.group(1) != "vods":
            raise HTTPException(
                status_code=400, detail="Invalid Range header: wrong item")

        content_range = {
            "item": match.group(1),
            "start": int(match.group(2)),
            "end": int(match.group(3)),
            "limit": int(match.group(3)) - int(match.group(2)) + 1
        }

        if content_range["start"] > content_range["end"]:
            raise HTTPException(
                status_code=400, detail="Invalid Range header: start cannot be greater than end")

        streams, total_streams = await self.service.search_streams(q, content_range)

        accept_ranges_header = f"Accept-Ranges: {content_range['item']}"
        content_range_header = f"Content-Range: {content_range['item']} {content_range['start']}-{content_range['end']}/{total_streams}"

        headers = [accept_ranges_header, content_range_header]

        return streams, headers

    async def update_stream_status(self, stream_id: str, status: str):
        try:
            result = await self.service.update_stream_status(stream_id, status)
        except InvalidId:
            raise HTTPException(
                status_code=404, detail=f"Stream ID {stream_id} is invalid")

        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")

        if result.status == "finished_transmuxing":
            await self.service.transcode_stream(stream_id)

        return result

    async def update_stream_tags(self, stream_id: str, tags: list[str], current_user: User):
        if not await self.service.can_modify_stream(stream_id, current_user):
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this stream")

        try:
            result = await self.service.update_stream_tags(stream_id, tags)
        except InvalidId:
            raise HTTPException(
                status_code=400, detail=f"Stream ID {stream_id} is invalid")

        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")

        return result

    async def update_stream_title(self, stream_id: str, title: str, current_user: User):
        if not await self.service.can_modify_stream(stream_id, current_user):
            raise HTTPException(
                status_code=403, detail="You are not allowed to update this stream")

        try:
            result = await self.service.update_stream_title(stream_id, title)
        except InvalidId:
            raise HTTPException(
                status_code=400, detail=f"Stream ID {stream_id} is invalid")

        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")

        return result

    async def list_streams(self, status: str = None):
        stream_list = await self.service.list_streams(status=status)
        if not stream_list:
            if status:
                raise HTTPException(
                    status_code=404, detail=f"No {status} streams found")
            else:
                raise HTTPException(status_code=404, detail="No streams found")

        return stream_list

    async def terminate_stream(self, stream_key: str):
        user_id = await self.service._getdel_stream_id_redis(stream_key)
        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
        stream_id = await self.service.get_live_stream_id(user_id)
        if not stream_id:
            raise HTTPException(
                status_code=404, detail="Stream not found")

        request = TransmuxerRequest(stream_id=stream_id, stream_key=stream_key)
        response = await self.service.stop_stream(request)

        await self.update_stream_status(stream_id, response.status)

        return response

    async def delete_stream(self, stream_id: str) -> bool:
        result = await self.service.delete_stream(stream_id)
        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")
