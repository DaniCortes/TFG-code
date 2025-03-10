import os

import httpx
from fastapi import HTTPException

from src.models.stream_model import Stream

STREAM_INFO_URL = os.getenv(
    "STREAM_INFO_URL", "http://stream-information-service:8000")


async def get_user_from_stream(stream_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{STREAM_INFO_URL}/streams/{stream_id}")
            response.raise_for_status()
            stream_data = response.json()
            stream = Stream(stream_id=stream_data['stream_id'],
                            user_id=stream_data['user_id'],
                            status=stream_data['status'])
            return stream

        except httpx.HTTPStatusError:
            detail = response.json().get("detail")
            raise HTTPException(
                status_code=response.status_code, detail=detail)
