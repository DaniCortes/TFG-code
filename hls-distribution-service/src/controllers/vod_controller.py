from fastapi import HTTPException
from fastapi.responses import FileResponse

from src.services.vod_service import VODService
from src.utils.exceptions import (FileNotFoundException,
                                  InvalidSegmentPathException)


class VODController:
    def __init__(self, vod_service: VODService):
        self.service = vod_service

    async def get_playlist(self, stream_id: str, quality: str = None, master: bool = False):
        if master and quality:
            raise HTTPException(
                status_code=400,
                detail="Cannot specify quality when requesting master playlist"
            )
        if not master and not quality:
            raise HTTPException(
                status_code=400,
                detail="Quality must be specified when requesting media playlist"
            )

        try:
            playlist_path = self.service.get_playlist_path(
                stream_id, quality, master)
            return FileResponse(
                playlist_path,
                media_type="application/vnd.apple.mpegurl",
                headers={"Cache-Control": "no-cache, no-store, private"}
            )
        except FileNotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_segment(self, stream_id: str, quality: str, segment_file: str):
        try:
            segment_path = self.service.get_segment_path(
                stream_id, quality, segment_file)

            return FileResponse(
                segment_path,
                media_type="video/mp4",
                headers={"Cache-Control": "no-cache, no-store, private",
                         "Accept-Ranges": "bytes"}
            )
        except FileNotFoundException as e:
            raise HTTPException(status_code=404, detail=e.message)

        except InvalidSegmentPathException as e:
            raise HTTPException(status_code=400, detail=e.message)

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def list_active_streams(self):
        return {"streams": []}
