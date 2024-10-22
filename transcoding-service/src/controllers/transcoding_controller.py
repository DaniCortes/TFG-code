# coding=utf-8

from fastapi import Depends, HTTPException
from services.transcoding_service import TranscodingService


_transcoding_service = None


def set_transcoding_service(transcoding_service: TranscodingService):
    global _transcoding_service
    _transcoding_service = transcoding_service


def get_transcoding_service() -> TranscodingService:
    if not _transcoding_service:
        raise RuntimeError("Transcoding service not set")
    return _transcoding_service


class TranscodingController:
    def __init__(self, service: TranscodingService = Depends(get_transcoding_service)):
        self.service = service

    def add_stream_to_transcode(self, stream_id: str, priority: bool = False):
        if not stream_id:
            raise HTTPException(
                status_code=400, detail="Stream ID is required")
        try:
            result = self.service.add_to_queue(stream_id, priority)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
