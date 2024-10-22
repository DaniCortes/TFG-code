from fastapi import APIRouter
from src.controllers.transmuxing_controller import TransmuxingController
from src.models.stream_models import StreamRequest, StreamResponse, StreamInfo

router = APIRouter()
transmuxing_controller = TransmuxingController()


@router.post("/streams", status_code=201, response_model=StreamResponse)
async def start_stream(request: StreamRequest):
    return await transmuxing_controller.start_stream(request)


@router.delete("/streams/{stream_id}", status_code=204, response_model=StreamResponse)
async def stop_stream(stream_id: str):
    return await transmuxing_controller.stop_stream(stream_id)
