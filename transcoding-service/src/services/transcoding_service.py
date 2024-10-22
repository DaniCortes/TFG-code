# coding=utf-8

import os
import httpx
import redis
import string
import asyncio
from src.utils.get_video_specs import get_video_specs
from src.models.stream_models import StreamResponse
from src.utils.exceptions import StreamInfoException, VideoResolutionFPSException


class TranscodingService:
    def __init__(self):
        self.HLS_SEGMENT_TIME = os.getenv('HLS_SEGMENT_TIME', 6)
        self.RTMP_INPUT_BASE = os.getenv(
            'RTMP_INPUT_BASE', 'rtmp://rtmp-ingest-service/live/')
        self.HLS_OUTPUT_BASE = os.getenv('HLS_OUTPUT_BASE', '/tmp/hls/')
        self.RECORDING_BASE = os.getenv('RECORDING_BASE', '/tmp/recordings/')
        self.PROFILES = [
            {'name': '1080p60', 'scale_width': 1920, 'scale_height': 1080,
                'fps': 60, 'bitrate': '6000k', 'maxrate': '6500k', 'bufsize': '10000k'},
            {'name': '1080p50', 'scale_width': 1920, 'scale_height': 1080,
                'fps': 50, 'bitrate': '6000k', 'maxrate': '6500k', 'bufsize': '10000k'},
            {'name': '1080p30', 'scale_width': 1920, 'scale_height': 1080,
                'fps': 30, 'bitrate': '4500k', 'maxrate': '5000k', 'bufsize': '7500k'},
            {'name': '720p60', 'scale_width': 1280, 'scale_height': 720,
                'fps': 60, 'bitrate': '4500k', 'maxrate': '5000k', 'bufsize': '7500k'},
            {'name': '720p50', 'scale_width': 1280, 'scale_height': 720,
                'fps': 50, 'bitrate': '4500k', 'maxrate': '5000k', 'bufsize': '7500k'},
            {'name': '720p30', 'scale_width': 1280, 'scale_height': 720,
                'fps': 30, 'bitrate': '3500k', 'maxrate': '4000k', 'bufsize': '4500k'},
            {'name': '480p30', 'scale-width': 854, 'scale_height': 481,
                'fps': 30, 'bitrate': '2500k', 'maxrate': '3000k', 'bufsize': '3500k', 'crop': 'crop=854:480:0:0:keep_aspect=1'},
            {'name': '480p25', 'scale-width': 854, 'scale_height': 481,
                'fps': 25, 'bitrate': '2500k', 'maxrate': '3000k', 'bufsize': '3500k', 'crop': 'crop=854:480:0:0:keep_aspect=1'}
        ]
        self.can_continue = True
        self.queue_process = None

        self.redis = redis.Redis(
            host='redis', port=6379, db=0, decode_responses=True)

    def add_to_queue(self, stream_id: str, priority: bool = False):
        if not priority:
            self.redis.lpush('streams', stream_id)
        else:
            self.redis.rpush('streams', stream_id)
        return StreamResponse(stream_id=stream_id, status="in_queue")

    async def start_queue_processing(self):
        self.can_continue = True
        self.queue_process = asyncio.create_task(self.__process_queue())

    async def __process_queue(self):
        while self.can_continue:
            if not self.redis.exists('currently_transcoding'):
                stream_id = await self.redis.rpop('streams')
                status = await self.__transcode_stream(stream_id)
                if status == "transcoded":
                    os.remove(f"{self.RECORDING_BASE}{stream_id}.mp4")

            await asyncio.sleep(5)

    async def __transcode_stream(self, stream_id: str):
        self.redis.set('currently_transcoding', stream_id)

        try:
            command = self.__generate_command(stream_id)

            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

            try:
                await self.__notify_stream_status(stream_id, "transcoding")
            except StreamInfoException:
                pass

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                status = "transcoded"

            else:
                status = "error_transcoding_ffmpeg"

        except VideoResolutionFPSException:
            status = "error_transcoding_resolution_fps"

        except FileNotFoundError:
            status = "error_transcoding_file_not_found"

        finally:
            try:
                await self.__notify_stream_status(stream_id, status)
            except StreamInfoException:
                pass

            self.redis.delete('currently_transcoding')
            return status

    def __set_profiles(self, file_path: str):
        video_info = get_video_specs(file_path)
        profiles_to_use = []

        if video_info["height"] >= 1080 or video_info["width"] >= 1920:
            if video_info["fps"] == 60:
                profiles_to_use.append(
                    self.PROFILES[0], self.PROFILES[3]), self.PROFILES[6]

            elif video_info["fps"] == 50:
                profiles_to_use.append(
                    self.PROFILES[1], self.PROFILES[4]), self.PROFILES[7]

            elif video_info["fps"] == 30:
                profiles_to_use.append(
                    self.PROFILES[2], self.PROFILES[5]), self.PROFILES[6]

        elif video_info["height"] >= 720 or video_info["width"] >= 1280:
            if video_info["fps"] == 60:
                profiles_to_use.append(self.PROFILES[3]), self.PROFILES[6]

            elif video_info["fps"] == 50:
                profiles_to_use.append(self.PROFILES[4]), self.PROFILES[7]

            elif video_info["fps"] == 30:
                profiles_to_use.append(self.PROFILES[5]), self.PROFILES[6]

        elif video_info["height"] >= 480 or video_info["width"] >= 854:
            if video_info["fps"] in [60, 30]:
                profiles_to_use.append(self.PROFILES[6])

            elif video_info["fps"] in [50, 25]:
                profiles_to_use.append(self.PROFILES[7])

        return profiles_to_use

    def __generate_command(self, stream_id: str, type="string"):
        input_file = f"{self.RECORDING_BASE}{stream_id}.mp4"

        if not os.path.isfile(input_file):
            raise FileNotFoundError

        profiles_to_use = self.__set_profiles(input_file)

        if not profiles_to_use:
            raise VideoResolutionFPSException(stream_id)

        output_base = f"{self.HLS_OUTPUT_BASE}{stream_id}"

        self.__create_folders(output_base, profiles_to_use)

        command = [
            "ffmpeg", "-loglevel", "fatal", "-i", input_file,
            "-filter_complex", f"\"[0:v]split={len(profiles_to_use)}"
        ]

        for profile in profiles_to_use:
            command[-1] += f"[{profile['name']}]"

        for profile in profiles_to_use:

            command[-1] += f";[{profile['name']}]scale=w={str(profile['scale_width'])}:h={str(profile['scale_height'])}:force_original_aspect_ratio=decrease,fps={str(profile['fps'])}"

            if "crop" in profile:
                command[-1] += f";crop={profile['crop']}"

            command[-1] += f"[{profile['name']}out];"

        command[-1] += "\""

        for i, profile in enumerate(profiles_to_use):
            command.extend([
                "-map", f"\"[{profile['name']}out]\"", "-map", "0:a",
                f"-c:v:{i}", "libvstav1", f"-b:v:{i}", profile['bitrate'],
                f"-maxrate:v:{i}", profile['maxrate'], f"-bufsize:v:{i}", profile['bufsize'],
                "-g", f"{profile['fps']*self.HLS_SEGMENT_TIME}", "-keyint_min", f"{profile['fps']*self.HLS_SEGMENT_TIME}", "-sc_threshold", "0",
                "-flags", "+cgop"
            ])

        command.extend([
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
            "-f", "hls", "-hls_time", f"{self.HLS_SEGMENT_TIME}", "-hls_playlist_type", "vod",
            "-hls_flags", "independent_segments",
            "-master_pl_name", "master.m3u8",
            "-hls_segment_type", "fmp4",
            "-hls_segment_filename",
            f"\"{output_base}/%v/stream_%v_%03d.mp4\"",
            "var_stream_map",
            f"\"v:0,a:0,name:{profiles_to_use[0]['name']}"])

        for i, profile in enumerate(profiles_to_use[1:], 1):
            command[-1] += f" v:{i},a:{i},name:{profile['name']}"

        command[-1] += f"\" {output_base}/%v/stream_%v.m3u8"

        if type == "list":
            return command

        command_str = " ".join(command)

        return command_str

    def __create_folders(self, output_base: str, profiles_to_use: list):
        for profile in profiles_to_use:
            os.makedirs(f"{output_base}/{profile['name']}", exist_ok=True)

    async def stop_queue_processing(self):
        self.should_continue = False

        if self.queue_process:
            await self.queue_process

        self.redis.close()

    async def __notify_stream_status(self, stream_id: str, status: str):
        try:
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.STREAM_INFO_SERVICE_URL}/streams/{stream_id}", json={"status": status})
        except httpx.HTTPStatusError as e:
            raise StreamInfoException(stream_id, e)
