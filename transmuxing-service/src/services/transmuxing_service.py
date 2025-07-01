import asyncio
import os
import shutil
from time import perf_counter

import httpx

from src.models.stream_models import StreamRequest, StreamResponse
from src.utils.exceptions import FFmpegProcessError, StreamNotFoundException
from src.utils.logger import logger


class TransmuxingService:
    def __init__(self):
        self.STREAM_INFORMATION_SERVICE_URL = os.getenv(
            'STREAM_INFORMATION_SERVICE_URL', 'http://stream-information-service:8000')
        self.HLS_SEGMENT_TIME = int(os.getenv("HLS_SEGMENT_TIME", "2"))
        self.HLS_LIST_SIZE = int(os.getenv("HLS_LIST_SIZE", "2"))
        self.HLS_OUTPUT_BASE = os.getenv('HLS_OUTPUT_BASE', '/tmp/hls/')
        self.RECORDING_OUTPUT_BASE = os.getenv(
            'RECORDING_OUTPUT_BASE', '/tmp/recordings/')
        self.RTMP_INGEST_SERVICE_URL = os.getenv(
            'RTMP_INGEST_SERVICE_URL', 'rtmp://rtmp-ingest-service/live/')
        self.active_streams: dict[str, set[asyncio.Task]] = {}
        self.processes: dict[str, set[asyncio.subprocess.Process]] = {}

    async def start_transmuxing(self, request: StreamRequest) -> StreamResponse:
        input_url = f"{self.RTMP_INGEST_SERVICE_URL}{request.stream_key}"
        output_base = f"{self.HLS_OUTPUT_BASE}{request.stream_id}"
        recording_file = f"{self.RECORDING_OUTPUT_BASE}{request.stream_id}.mp4"

        os.makedirs(output_base, exist_ok=True)
        os.makedirs(os.path.dirname(recording_file), exist_ok=True)
        logger.info(f"Folder created: {output_base}")

        command = [
            'ffmpeg', '-loglevel', 'debug',
            '-re', '-i', input_url,
            '-map', '0:a', '-map', '0:v',
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'hls',
            '-hls_time', f'{self.HLS_SEGMENT_TIME}',
            '-hls_list_size', f'{self.HLS_LIST_SIZE}',
            '-hls_allow_cache', '0',
            '-hls_segment_type', 'fmp4',
            '-hls_segment_filename', f'{output_base}/%d.mp4',
            '-hls_flags', 'delete_segments+append_list',
            '-master_pl_name', 'master.m3u8',
            f"{output_base}/stream.m3u8",
            '-f', 'mp4',
            '-movflags', '+frag_keyframe+empty_moov+faststart',
            recording_file,
        ]

        thumbnail_command = [
            'ffmpeg', '-loglevel', 'debug',
            '-i', input_url,
            '-f', 'image2',
            '-vf', r'fps=1/15',
            '-c:v', 'libwebp',
            '-update', '1',
            f'{output_base}/thumbnail.webp'
        ]

        main_task = asyncio.create_task(
            self.__run_ffmpeg(request.stream_id, command))

        thumbnail_task = asyncio.create_task(
            self.__run_ffmpeg(request.stream_id, thumbnail_command))

        self.active_streams[request.stream_id] = {main_task, thumbnail_task}

        return StreamResponse(stream_id=request.stream_id, status="live")

    async def __run_ffmpeg(self, stream_id: str, command: list[str]):
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            if not self.processes.get(stream_id):
                self.processes[stream_id] = set()

            self.processes[stream_id].add(process)

            stdout, stderr = await process.communicate()

            if process.returncode != 0 and process.returncode != 255:
                logger.error(
                    f"FFmpeg process for stream {stream_id} failed with return code {process.returncode}")

                raise FFmpegProcessError(stream_id, stderr.decode())

        except FFmpegProcessError as e:
            logger.error(f"FFmpeg process error: {e}")
            await self.__notify_stream_service(stream_id, "error_transmuxing")

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await self.__notify_stream_service(stream_id, "error_transmuxing")

    def remove_contents_from_directory(self, directory: str):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)

                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            except Exception as e:
                logger.error(
                    f"Failed to delete {file_path} : {str(e)}")
                print(f"Failed to delete {file_path} : {str(e)}")

    async def _stop_transmuxing(self, stream_id: str):
        if stream_id not in self.active_streams:
            raise StreamNotFoundException(stream_id)

        if stream_id in self.processes:
            processes = self.processes.get(stream_id)

            del self.processes[stream_id]

            for process in processes:
                if process.returncode is None:
                    await process.wait()

        if stream_id in self.active_streams:
            tasks = self.active_streams[stream_id]

            del self.active_streams[stream_id]

            for task in tasks:
                if not task.done():
                    task.cancel()
                try:
                    await task
                except asyncio.CancelledError as e:
                    pass

        if ((int(self.HLS_SEGMENT_TIME) + int(self.HLS_LIST_SIZE))*2) > 10:
            await asyncio.sleep((self.HLS_SEGMENT_TIME + self.HLS_LIST_SIZE) * 2 + 10)
        else:
            await asyncio.sleep(10)

        self.remove_contents_from_directory(
            f"{self.HLS_OUTPUT_BASE}{stream_id}")
        logger.debug(
            f"Removed contents from directory: {self.HLS_OUTPUT_BASE}{stream_id}")

        await self.__notify_stream_service(stream_id, "finished_transmuxing")

    async def __notify_stream_service(self, stream_id: str, status: str):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(f"{self.STREAM_INFORMATION_SERVICE_URL}/streams/{stream_id}/status", json={"status": status})
                response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(
                f"Failed to notify stream service for stream {stream_id}")
            print(f"Failed to notify stream service for stream {stream_id}")
        except Exception as e:
            logger.error(
                f"Failed to notify stream service for stream {stream_id} (general): {str(e)}")
            print(
                f"Failed to notify stream service for stream {stream_id}: {str(e)}")
