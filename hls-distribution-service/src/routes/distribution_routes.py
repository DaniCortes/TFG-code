from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from controllers.distribution_controller import StreamController

router = APIRouter()
stream_controller = StreamController()


@router.get("/streams/{stream_key}/playlist.m3u8")
async def get_playlist(stream_key: str):
    return await stream_controller.get_playlist(stream_key)


@router.get("/streams/{stream_key}/segments/{segment_file}")
async def get_segment(stream_key: str, segment_file: str):
    return await stream_controller.get_segment(stream_key, segment_file)


@router.get("/streams")
async def list_active_streams():
    return await stream_controller.list_active_streams()
