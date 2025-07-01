from fastapi import HTTPException
from fastapi.responses import FileResponse

from src.services.live_service import LiveService
from src.utils.exceptions import InvalidSegmentPathException


class LiveController:
    def __init__(self, live_service: LiveService):
        self.service = live_service

    async def list_active_streams(self):
        return self.service.list_active_streams()

    async def get_playlist(self, stream_id: str, master: bool = False):
        try:
            playlist_path = self.service.get_playlist_path(stream_id, master)
            return FileResponse(
                playlist_path,
                media_type="application/vnd.apple.mpegurl",
                headers={"Cache-Control": "no-cache, no-store, private",
                         "Accept-Ranges": "bytes"}
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Stream not found")

    async def get_raw(self, stream_id: str):
        try:
            raw_path = self.service.get_raw_path(stream_id)
            return FileResponse(
                raw_path,
                media_type="video/mp4",
                headers={"Cache-Control": "no-cache, no-store, private"}
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Stream not found")

    async def get_segment(self, stream_id: str, segment_file: str):
        try:
            segment_path = self.service.get_segment_path(
                stream_id, segment_file)

            return FileResponse(
                segment_path,
                media_type="video/mp4",
                headers={
                    "Cache-Control": "no-cache, no-store, private",
                    "Accept-Ranges": "bytes"
                }
            )
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.args[0])

        except InvalidSegmentPathException as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def list_active_streams(self):
        return {"streams": []}
