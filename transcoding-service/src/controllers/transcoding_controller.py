from fastapi import HTTPException

from src.services.transcoding_service import TranscodingService
from src.utils.logger import logger


class TranscodingController:
    def __init__(self, transcoding_service: TranscodingService):
        self.service = transcoding_service

    async def add_stream_to_transcode(self, stream_id: str, priority: bool = False):
        if not stream_id:
            raise HTTPException(
                status_code=400, detail="Stream ID is required")
        try:
            result = await self.service.add_to_queue(stream_id, priority)
            logger.debug(
                f"Controller: Stream {stream_id} added to queue with priority {priority}")
            return result
        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
