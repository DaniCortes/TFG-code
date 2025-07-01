from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, Response
from fastapi.responses import FileResponse
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
    logger.debug(f"Received {call} request for stream key {stream_key}")

    if call == "publish":
        await controller.create_stream(stream_key)

    else:
        await controller.terminate_stream(stream_key)


@router.get("/streams", response_model=list[Stream])
async def list_streams():
    return await controller.list_streams()


@router.get("/streams/live/{user_id}", response_model=Stream)
async def get_user_stream(user_id: str):
    return await controller.get_live_stream(user_id=user_id)


@router.get("/streams/live", response_model=list[Stream])
async def list_live_streams():
    return await controller.list_streams(status="live")


@router.get("/streams/transcoded", response_model=list[Stream])
async def list_transcoded_streams():
    return await controller.list_streams(status="transcoded")


@router.get("/search/livestreams", response_model=list[Stream])
async def search_livestreams(response: Response, q: str, range: str = Header(...)):
    streams, headers = await controller.search_streams(q, range, "livestreams")
    for header in headers:
        response.headers[header.split(":")[0]] = header.split(":")[1].strip()

    return streams


@router.get("/search/vods", response_model=list[Stream])
async def search_vods(response: Response, q: str, range: str = Header(...)):
    streams, headers = await controller.search_streams(q, range, "vods")
    for header in headers:
        response.headers[header.split(":")[0]] = header.split(":")[1].strip()

    return streams


@router.get("/streams/{stream_id}", response_model=Stream)
async def get_stream(stream_id: str):
    return await controller.get_stream(stream_id=stream_id)


@router.get("/streams/{stream_id}/thumbnail.webp", response_class=FileResponse)
async def get_stream_thumbnail(stream_id: str):
    return controller.get_stream_thumbnail(stream_id=stream_id)


@router.patch("/streams/{stream_id}/status", status_code=200, response_model=Stream)
async def update_stream(stream_id: str, status_request: StatusRequest):
    return await controller.update_stream_status(stream_id, status_request.status)


@router.patch("/streams/{stream_id}/visibility", status_code=200, response_model=Stream)
async def update_stream(stream_id: str, visibility_request: StatusRequest, current_user: User = Depends(get_current_user)):
    return await controller.update_stream_visibility(stream_id, visibility_request.status, current_user)


@router.patch("/streams/{stream_id}/tags", status_code=200, response_model=Stream)
async def update_stream_tags(stream_id: str, tags_request: TagsRequest, current_user: User = Depends(get_current_user)):
    return await controller.update_stream_tags(stream_id, tags_request.tags, current_user)


@router.patch("/streams/{stream_id}/title", status_code=200, response_model=Stream)
async def update_stream_title(stream_id: str, title: str, current_user: User = Depends(get_current_user)):
    return await controller.update_stream_title(stream_id, title, current_user)


@router.delete("/streams/{stream_id}", status_code=200)
async def delete_stream(stream_id: str):
    return await controller.delete_stream(stream_id)
