class InvalidSegmentPathException(Exception):
    """Exception raised for invalid segment paths in HLS distribution service."""

    def __init__(self, message="Invalid segment path provided"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class FileNotFoundException(Exception):
    """Exception raised for file not found in HLS distribution service."""

    def __init__(self, message="File not found"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"
