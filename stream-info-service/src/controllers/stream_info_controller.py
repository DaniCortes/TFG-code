from src.services.stream_info_service import StreamService
from src.utils.postgresql_utils import get_user_by_stream_key
from src.utils.exceptions import TransmuxerException, UserAlreadyStreamingException
from fastapi.exceptions import HTTPException


class StreamController:
    def __init__(self):
        self.service = StreamService()

    async def create_stream(self, stream_key: str):
        user = await get_user_by_stream_key(stream_key)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.account_status != "active":
            raise HTTPException(
                status_code=403, detail="User account is not active")

        try:
            return await self.service.create_stream(user)

        except UserAlreadyStreamingException as e:
            raise HTTPException(status_code=403, detail=str(e))

        except TransmuxerException as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_stream(self, stream_id: str):
        return await self.service.get_stream(stream_id)

    async def transcode_stream(self, stream_key: str):
        user = await get_user_by_stream_key(stream_key)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await self.service.transcode_stream(user)

    async def update_stream_status(self, stream_id: str, status: str):
        result = await self.service.update_stream_status(stream_id, status)

        if not result:
            raise HTTPException(status_code=404, detail="Stream not found")

        return result

    async def list_streams(self, filter: str = None):
        return await self.service.list_streams(filter)
