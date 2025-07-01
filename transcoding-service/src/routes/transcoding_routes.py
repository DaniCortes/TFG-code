from fastapi import APIRouter

from src.controllers.transcoding_controller import TranscodingController
from src.models.stream_models import StreamRequest, StreamResponse
from src.services.transcoding_service import TranscodingService

router = APIRouter()

transcoding_service = TranscodingService()
transcoding_controller = TranscodingController(transcoding_service)


@router.post("/streams", status_code=201, response_model=StreamResponse)
async def add_stream_to_transcode(request: StreamRequest):
    return await transcoding_controller.add_stream_to_transcode(request.stream_id, request.priority)
