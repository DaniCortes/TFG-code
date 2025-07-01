from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.controllers.live_controller import LiveController
from src.services.live_service import LiveService

router = APIRouter()
live_service = LiveService()
live_controller = LiveController(live_service)


@router.get("/live/{stream_id}/master.m3u8", response_class=FileResponse)
async def get_playlist(stream_id: str):
    return await live_controller.get_playlist(stream_id, master=True)


@router.get("/live/{stream_id}/stream.m3u8", response_class=FileResponse)
async def get_live_playlist(stream_id: str):
    return await live_controller.get_playlist(stream_id)


@router.get("/live/debug/{stream_id}", response_class=FileResponse)
async def debug_stream(stream_id: str):
    return await live_controller.get_raw(stream_id)


@router.get("/live/{stream_id}/{segment_file}", response_class=FileResponse)
async def get_segment(stream_id: str, segment_file: str):
    return await live_controller.get_segment(stream_id, segment_file)
