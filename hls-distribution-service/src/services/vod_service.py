import os
from pathlib import Path

from src.utils.exceptions import (FileNotFoundException,
                                  InvalidSegmentPathException)


class VODService:
    def __init__(self):
        self.BASE_PATH = os.getenv("HLS_STREAM_BASE", "/tmp/hls")

    def get_playlist_path(self, stream_id: str, quality: str, master: bool) -> str:
        if master:
            playlist_path = Path(self.BASE_PATH) / stream_id / "master.m3u8"
        else:
            playlist_path = Path(self.BASE_PATH) / \
                stream_id / quality / "stream.m3u8"

        if not playlist_path.exists():
            if master:
                playlist_type = "Master"
            else:
                playlist_type = f"{quality}"

                raise FileNotFoundException(
                    message=f"{playlist_type} playlist not found for stream {stream_id}")

        return str(playlist_path)

    def get_segment_path(self, stream_id: str, quality: str, segment_file: str) -> str:
        if '..' in segment_file or '/' in segment_file:
            raise InvalidSegmentPathException()

        stream_path = Path(self.BASE_PATH) / stream_id

        if not stream_path.exists():
            raise FileNotFoundException(
                message=f"Stream not found: {stream_id}")

        quality_path = stream_path / quality

        if not quality_path.exists():
            raise FileNotFoundException(
                message=f"Quality not found for stream {stream_id}: {quality}")

        segment_path = stream_path / quality / segment_file

        if not segment_path.exists():
            raise FileNotFoundException(
                message=f"Segment not found: {segment_file}")

        return str(segment_path)
