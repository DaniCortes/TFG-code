class TranscoderNofifyException(Exception):
    def __init__(self, stream_id: str, error: str):
        self.message = f"Stream {stream_id} successfully stopped but failed to notify transcoding service: {error}"
        super().__init__(self.message)


class StreamNotFoundException(Exception):
    def __init__(self, stream_id: str):
        self.message = f"Stream {stream_id} not found"
        super().__init__(self.message)
