import asyncio
import os
import shutil

import httpx
from src.models.stream_models import StreamRequest, StreamResponse
from src.utils.exceptions import FFmpegProcessError, StreamNotFoundException


class TransmuxingService:
    def __init__(self):
        self.HLS_SEGMENT_TIME = int(os.getenv("HLS_SEGMENT_TIME", "6"))
        self.HLS_OUTPUT_BASE = os.getenv('HLS_OUTPUT_BASE', '/tmp/hls/')
        self.RECORDING_OUTPUT_BASE = os.getenv(
            'RECORDING_OUTPUT_BASE', '/tmp/recordings/')
        self.RTMP_INGEST_SERVICE_URL = os.getenv(
            'RTMP_INGEST_SERVICE_URL', 'rtmp://rtmp-ingest-service/live/')
        self.active_streams: dict[str, asyncio.Task] = {}
        self.processes: dict[str, asyncio.subprocess.Process] = {}

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
            '-hls_time', f'{self.HLS_SEGMENT_TIME}',
            '-hls_list_size', '6',
            '-hls_segment_type', 'fmp4',
            '-hls_segment_filename', f"{output_base}/%d.mp4",
            '-hls_flags', 'delete_segments+append_list',
            f"{output_base}/playlist.m3u8",
            '-f', 'mp4',
            '-movflags', '+frag_keyframe+empty_moov+faststart',
            recording_file
        ]

        task = asyncio.create_task(
            self.__run_ffmpeg(request.stream_id, command))

        self.active_streams[request.stream_id] = task

        return StreamResponse(stream_id=request.stream_id, status="live")

    async def __run_ffmpeg(self, stream_id: str, command: list[str]):
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            self.processes[stream_id] = process

            stdout, stderr = await process.communicate()

            if process.returncode != 0 and stderr:
                raise FFmpegProcessError(stream_id, stderr.decode())

        except FFmpegProcessError:
            await self.__notify_stream_service(stream_id, "error_transmuxing")

        except Exception:
            pass

        finally:
            if stream_id in self.processes:
                del self.processes[stream_id]

            if stream_id in self.active_streams:
                del self.active_streams[stream_id]

            self.remove_contents_from_directory(
                f"{self.HLS_OUTPUT_BASE}{stream_id}")

    def remove_contents_from_directory(self, directory: str):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)

                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            except Exception as e:
                print(f"Failed to delete {file_path} : {str(e)}")

    async def stop_transmuxing(self, stream_id: str) -> StreamResponse:
        if stream_id not in self.active_streams:
            raise StreamNotFoundException(stream_id)

        process = self.processes.get(stream_id)

        if process:
            del self.processes[stream_id]
            try:
                process.terminate()

                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)

                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()

            except ProcessLookupError:
                pass

        task = self.active_streams[stream_id]

        if task:
            del self.active_streams[stream_id]

            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        await self.__notify_stream_service(stream_id, "terminated")

    async def __notify_stream_service(self, stream_id: str, status: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(f"http://stream-info-service:8000/streams/status/{stream_id}", json={"status": status})
                response.raise_for_status()
        except httpx.HTTPStatusError:
            print(f"Failed to notify stream service for stream {stream_id}")
        except Exception:
            print(f"Failed to notify stream service for stream {stream_id}")
