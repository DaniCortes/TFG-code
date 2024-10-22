import os
import subprocess
from typing import List

import httpx
from src.models.stream_models import StreamRequest, StreamResponse
from src.utils.exceptions import StreamNotFoundException


class TransmuxingService:
    def __init__(self):
        self.HLS_OUTPUT_BASE = os.getenv('HLS_OUTPUT_BASE', '/ tmp/hls/')
        self.RECORDING_OUTPUT_BASE = os.getenv(
            'RECORDING_OUTPUT_BASE', '/tmp/recordings/')
        self.RTMP_INGEST_SERVICE_URL = os.getenv(
            'RTMP_INGEST_SERVICE_URL', 'rtmp://rtmp-ingest-service/live/')
        self.http_client = httpx.AsyncClient()
        self.active_streams: dict[str, subprocess.Popen] = {}

    async def start_transmuxing(self, request: StreamRequest) -> StreamResponse:
        input_url = f"{self.RTMP_INGEST_SERVICE_URL}{request.stream_key}"
        output_base = f"{self.HLS_OUTPUT_BASE}{request.stream_id}"
        recording_file = f"{self.RECORDING_OUTPUT_BASE}{request.stream_id}.mp4"

        os.makedirs(output_base, exist_ok=True)
        os.makedirs(os.path.dirname(recording_file), exist_ok=True)

        command = [
            'ffmpeg', '-loglevel', 'fatal',
            '-i', input_url,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'hls',
            '-hls_time', '6',
            '-hls_list_size', '6',
            '-hls_segment_type', 'fmp4',
            '-hls_flags', 'delete_segments+append_list',
            f"{output_base}/playlist.m3u8",
            '-f', 'mp4',
            '-movflags', '+frag_keyframe+empty_moov+faststart',
            recording_file
        ]

        process = subprocess.Popen(command)

        self.active_streams[request.stream_id] = process

        return StreamResponse(stream_id=request.stream_id, status="live")

    async def stop_transmuxing(self, stream_id: str):
        if not stream_id in self.active_streams:
            raise StreamNotFoundException(stream_id)

        process = self.active_streams.pop(stream_id)
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        return StreamResponse(stream_id=stream_id, status="terminated")
