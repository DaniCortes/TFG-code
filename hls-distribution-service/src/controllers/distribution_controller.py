from fastapi import HTTPException
from fastapi.responses import FileResponse
from src.services.distribution_service import StreamService


class StreamController:
    def __init__(self):
        self.stream_service = StreamService()

    async def get_playlist(self, stream_key: str):
        try:
            playlist_path = await self.stream_service.get_playlist_path(stream_key)
            return FileResponse(
                playlist_path,
                media_type="application/vnd.apple.mpegURL",
                headers={"Cache-Control": "no-cache"}
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Stream not found")

    async def get_segment(self, stream_key: str, segment_file: str):
        try:
            segment_path = await self.stream_service.get_segment_path(stream_key, segment_file)
            return FileResponse(
                segment_path,
                media_type="video/mp4",
                headers={"Cache-Control": "no-cache",
                         "Content-Disposition": f"inline; filename={segment_file}"}
            )
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Segment not found")
