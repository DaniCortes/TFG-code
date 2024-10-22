class TransmuxerException(Exception):
    def __init__(self, stream_id: str, error: str):
        self.message = f"Stream {stream_id} could not be transmuxed or recorded: {error}"
        super().__init__(self.message)


class TranscoderException(Exception):
    def __init__(self, stream_id: str, error: str):
        self.message = f"Stream {stream_id} could not be transcoded: {error}"
        super().__init__(self.message)


class StreamNotFoundException(Exception):
    def __init__(self):
        self.message = "Stream not found"
        super().__init__(self.message)


class UserAlreadyStreamingException(Exception):
    def __init__(self, user_id: str):
        self.message = f"User {user_id} is already streaming"
        super().__init__(self.message)
