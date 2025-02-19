from fastapi import HTTPException

from src.models.stream_models import StreamRequest, StreamResponse
from src.models.user_model import User
from src.services.transmuxing_service import TransmuxingService
from src.utils.exceptions import StreamNotFoundException
from src.utils.logger import logger


class TransmuxingController:
    def __init__(self, transmuxing_service: TransmuxingService):
        self.service = transmuxing_service

    async def start_stream(self, request: StreamRequest):
        empty_params = [param for param, value in request.model_dump(
        ).items() if value is None or value == ""]

        if empty_params:
            logger.debug(f"Empty parameters: {empty_params}")
            raise HTTPException(
                status_code=400, detail=f"The following parameters cannot be empty: {', '.join(empty_params)}")

        try:
            stream_response = await self.service.start_transmuxing(request)

        except ValueError as ve:
            raise HTTPException(
                status_code=400, detail="Invalid stream key: " + str(ve))

        except OSError as e:
            raise HTTPException(
                status_code=500, detail="File system error: " + str(e))

        except Exception as e:
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred: " + str(e))

        if not stream_response:
            raise HTTPException(
                status_code=500, detail="Failed to start stream")
        return stream_response

    async def stop_stream(self, stream_id: str, current_user: User):
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403, detail="You are not authorized to perform this action")

        try:
            await self.service.stop_transmuxing(stream_id)

        except StreamNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))

        except Exception as e:
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred: " + str(e))
