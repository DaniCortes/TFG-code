import os
from pathlib import Path
from fastapi import HTTPException


class StreamService:
    def __init__(self):
        self.base_path = os.getenv("HLS_STREAM_BASE", "/tmp/hls")

    async def get_playlist_path(self, stream_key: str) -> str:
        playlist_path = Path(self.base_path) / stream_key / "playlist.m3u8"
        if not playlist_path.exists():
            raise FileNotFoundError(
                f"Playlist not found for stream: {stream_key}")
        return str(playlist_path)

        return os.path.join(self.base_path, stream_key, "playlist.m3u8")

    async def get_segment_path(self, stream_key: str, segment_file: str) -> str:
        # Validate segment file name to prevent directory traversal
        if '..' in segment_file or '/' in segment_file:
            raise HTTPException(
                status_code=400, detail="Invalid segment file name")

        segment_path = Path(self.base_path) / stream_key / segment_file
        if not segment_path.exists():
            raise FileNotFoundError(f"Segment not found: {segment_file}")
        return str(segment_path)
