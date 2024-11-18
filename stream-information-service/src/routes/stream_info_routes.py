from typing import Annotated

from fastapi import APIRouter, Depends, Form

from src.controllers.stream_info_controller import StreamController
from src.models.stream_models import (IngestRequest, StatusRequest, Stream,
                                      TagsRequest)
from src.models.user_model import User
from src.services.stream_info_service import StreamService
from src.utils.logger import logger
from src.utils.token_utils import get_current_user

router = APIRouter()

service = StreamService()
controller = StreamController(service)


@router.post("/streams", status_code=201)
async def create_or_terminate_stream(request: Annotated[IngestRequest, Form()]):
    call = request.call
    stream_key = request.name
    logger.debug(f"Received {call} request for stream {stream_key}")

    if call == "publish":
        await controller.create_stream(stream_key)

    else:
        await controller.transcode_stream(stream_key)


@router.get("/streams", response_model=list[Stream])
async def list_streams():
    return await controller.list_streams()


@router.get("/streams/{stream_id}", response_model=Stream)
async def get_stream(stream_id: str):
    return await controller.get_stream(stream_id)


@router.patch("/streams/status/{stream_id}", status_code=200, response_model=Stream)
async def update_stream(stream_id: str, status_request: StatusRequest):
    return await controller.update_stream_status(stream_id, status_request.status)


@router.patch("/streams/tags/{stream_id}", status_code=200, response_model=Stream)
async def update_stream_tags(stream_id: str, tags_request: TagsRequest, current_user: User = Depends(get_current_user)):
    return await controller.update_stream_tags(stream_id, tags_request.tags, current_user)
