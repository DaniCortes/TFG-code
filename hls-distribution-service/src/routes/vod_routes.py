from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.controllers.vod_controller import VODController
from src.services.vod_service import VODService

router = APIRouter()
vod_service = VODService()
vod_controller = VODController(vod_service)


@router.get("/vod/{stream_id}/master.m3u8", response_class=FileResponse)
async def get_playlist(stream_id: str):
    return await vod_controller.get_playlist(stream_id, master=True)


@router.get("/vod/{stream_id}/{quality}/stream.m3u8", response_class=FileResponse)
async def get_playlist(stream_id: str, quality: str):
    return await vod_controller.get_playlist(stream_id, quality)


@router.get("/vod/{stream_id}/{quality}/{segment_file}", response_class=FileResponse)
async def get_segment(stream_id: str, quality: str, segment_file: str):
    return await vod_controller.get_segment(stream_id, quality, segment_file)
