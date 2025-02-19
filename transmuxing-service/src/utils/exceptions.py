class StreamNotFoundException(Exception):
    def __init__(self, stream_id: str):
        self.message = f"Stream {stream_id} not found"
        super().__init__(self.message)


class FFmpegProcessError(Exception):
    def __init__(self, stream_id: str, error: str):
        self.message = f"Failed FFmpeg process for stream {stream_id}: {error}"
        super().__init__(self.message)
