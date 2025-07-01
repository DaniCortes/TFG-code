from fastapi import APIRouter, Depends, HTTPException

from src.controllers.transmuxing_controller import TransmuxingController
from src.models.stream_models import StreamRequest, StreamResponse
from src.models.user_model import User
from src.services.transmuxing_service import TransmuxingService
from src.utils.logger import logger
from src.utils.token_utils import get_current_user

router = APIRouter()
service = TransmuxingService()
controller = TransmuxingController(service)


@router.post("/streams", status_code=201, response_model=StreamResponse)
async def start_stream(request: StreamRequest):
    try:
        return await controller.start_stream(request)
    except HTTPException as e:
        logger.debug(str(e))
        raise e


@router.delete("/streams", status_code=200, response_model=StreamResponse)
async def terminate_stream(request: StreamRequest):
    return await controller.stop_stream(request.stream_id, User(is_admin=True))


@router.delete("/streams/live/{stream_id}", status_code=200, response_model=StreamResponse)
async def stop_stream(stream_id: str, current_user: User = Depends(get_current_user)):
    return await controller.stop_stream(stream_id, current_user)
