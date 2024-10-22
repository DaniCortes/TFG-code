class StreamInfoException(Exception):
    def __init__(self, stream_id: str, error: str):
        self.message = f"Failed to notify stream {stream_id} status to the Stream Info Service: {error}"
        super().__init__(self.message)


class VideoResolutionFPSException(Exception):
    def __init__(self, stream_id: str):
        self.message = f"Video resolution or framerate of {stream_id} not supported"
        super().__init__(self.message)
