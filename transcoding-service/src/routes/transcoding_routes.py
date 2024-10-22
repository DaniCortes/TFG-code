# coding=utf-8

from fastapi import APIRouter
from src.controllers.transcoding_controller import TranscodingController
from src.models.stream_models import StreamResponse

router = APIRouter()
transcoding_controller = TranscodingController()


@router.post("/streams", status_code=201, response_model=StreamResponse)
async def add_stream_to_transcode(stream_id: str, priority: bool = False):
    return await transcoding_controller.add_stream_to_transcode(stream_id, priority)
