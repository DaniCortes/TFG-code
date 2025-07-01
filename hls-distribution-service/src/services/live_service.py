import os
from pathlib import Path

from src.utils.exceptions import InvalidSegmentPathException


class LiveService:
    def __init__(self):
        self.BASE_PATH = os.getenv("HLS_STREAM_BASE", "/tmp/hls")
        self.RECORD_PATH = os.getenv("RECORD_BASE", "/tmp/recordings")

    def get_playlist_path(self, stream_id: str, master: bool = False) -> str:
        if master:
            playlist_path = Path(self.BASE_PATH) / stream_id / "master.m3u8"
        else:
            playlist_path = Path(self.BASE_PATH) / stream_id / "stream.m3u8"

        if not playlist_path.exists():
            raise FileNotFoundError(
                f"Playlist not found for stream: {stream_id}")

        return str(playlist_path)

    def get_raw_path(self, stream_id: str) -> str:
        raw_path = Path(self.RECORD_PATH) / f"{stream_id}.mp4"

        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw stream not found for stream: {stream_id}")

        return str(raw_path)

    def get_segment_path(self, stream_key: str, segment_file: str) -> str:
        if '..' in segment_file or '/' in segment_file:
            raise InvalidSegmentPathException()

        segment_path = Path(self.BASE_PATH) / stream_key / segment_file

        if not segment_path.exists():
            raise FileNotFoundError(f"Segment not found: {segment_file}")

        return str(segment_path)
