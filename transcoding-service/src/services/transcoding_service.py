import asyncio
import os
from datetime import time
from typing import Any

import httpx
from fastapi import HTTPException
from redis import asyncio as aioredis
from src.models.stream_models import StreamResponse
from src.utils.exceptions import (StreamInfoException,
                                  ThumbnailGenerationException,
                                  VideoResolutionFPSException)
from src.utils.get_video_specs import get_video_specs
from src.utils.logger import logger


class TranscodingService:
    def __init__(self):
        self.STREAM_INFO_SERVICE_URL = os.getenv(
            "STREAM_INFO_SERVICE_URL", "http://stream-information-service:8000")
        self.HLS_SEGMENT_TIME = int(os.getenv("HLS_SEGMENT_TIME", "6"))
        self.RTMP_INPUT_BASE = os.getenv(
            "RTMP_INPUT_BASE", "rtmp://rtmp-ingest-service/live/")
        self.HLS_OUTPUT_BASE = os.getenv("HLS_OUTPUT_BASE", "/tmp/hls/")
        self.RECORDING_BASE = os.getenv("RECORDING_BASE", "/tmp/recordings/")
        self.PROFILES = [
            {"name": "1080p60", "scale_width": 1920, "scale_height": 1080,
                "fps": 60, "maxbitrate": "6000k"},
            {"name": "1080p50", "scale_width": 1920, "scale_height": 1080,
                "fps": 50, "maxbitrate": "6000k"},
            {"name": "1080p30", "scale_width": 1920, "scale_height": 1080,
                "fps": 30, "maxbitrate": "4500k"},
            {"name": "720p60", "scale_width": 1280, "scale_height": 720,
                "fps": 60, "maxbitrate": "4500k"},
            {"name": "720p50", "scale_width": 1280, "scale_height": 720,
                "fps": 50, "maxbitrate": "4500k"},
            {"name": "720p30", "scale_width": 1280, "scale_height": 720,
                "fps": 30, "maxbitrate": "3500k"},
            {"name": "480p30", "scale_width": 854, "scale_height": 481,
                "fps": 30, "maxbitrate": "2500k", "crop": "854:480:0:0:keep_aspect=1"},
            {"name": "480p25", "scale_width": 854, "scale_height": 481,
                "fps": 25, "maxbitrate": "2500k", "crop": "854:480:0:0:keep_aspect=1"}
        ]
        self.can_continue = True
        self.queue_process = asyncio.create_task(self.__process_queue())

        self.redis = aioredis.Redis(
            host="redis", port=6379, db=0, decode_responses=True)

    async def add_to_queue(self, stream_id: str, priority: bool = False):
        if not priority:
            await self.redis.lpush("streams", stream_id)
        else:
            await self.redis.rpush("streams", stream_id)
        logger.debug(
            f"Service: Stream {stream_id} added to queue with priority {priority}")
        return StreamResponse(stream_id=stream_id, status="in_queue")

    async def __process_queue(self):
        logger.debug("Service: Starting queue processing...")
        await self.redis.delete("currently_transcoding")
        while self.can_continue:
            logger.debug("Service: Processing queue...")
            stream_id = await self.redis.get("currently_transcoding")
            # await self.redis.exists("currently_transcoding"):
            if not stream_id:
                logger.debug(
                    "Service: No stream currently transcoding, looking for stream to transcode.")
                stream_id = await self.redis.rpop("streams")
                if stream_id:
                    logger.debug("Service: Found stream to transcode.")
                    status = await self.__transcode_stream(stream_id)

                    if status == "transcoded":
                        os.remove(f"{self.RECORDING_BASE}{stream_id}.mp4")
                        logger.debug(
                            f"Service: Stream {stream_id} transcoded successfully and recording file removed.")
                else:
                    logger.debug("Service: No streams in queue. Sleeping...")
                    await asyncio.sleep(5)

            else:
                logger.debug(
                    f"Service: Stream {stream_id} currently transcoding, waiting for it to finish.")
                await asyncio.sleep(5)

    async def __transcode_stream(self, stream_id: str):
        await self.redis.set("currently_transcoding", stream_id)
        logger.debug(
            f"Service: Stream {stream_id} is going to be transcoded.")

        output_base = f"{self.HLS_OUTPUT_BASE}{stream_id}"
        status = "error_transcoding_internal"

        try:
            await self.__generate_thumbnail(stream_id)
            if not os.path.exists(output_base + "/thumbnail.webp"):
                await self.__generate_thumbnail(stream_id, fallback=True)
            command = self.__generate_command(stream_id, type="list")

            logger.debug(
                f"Service: Command to be executed: {" ".join(command)}")
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=output_base
            )
            await self.__notify_stream_status(stream_id, "transcoding")
            stdout, stderr = await process.communicate()
            '''logger.debug(
                f"Service: Transcoding process finished with stdout: {stdout.decode()} and stderr: {stderr.decode()}")'''

            if process.returncode == 0:
                status = "transcoded"

            else:
                status = "error_transcoding_ffmpeg"

        except VideoResolutionFPSException:
            status = "error_transcoding_resolution_fps"

        except FileNotFoundError:
            status = "error_transcoding_file_not_found"

        except ThumbnailGenerationException:
            status = "error_transcoding_thumbnail_generation"

        except Exception as e:
            raise HTTPException(
                detail=f"Error transcoding stream {stream_id}: {str(e)}"
            )

        finally:
            try:
                await self.__notify_stream_status(stream_id, status)
            except StreamInfoException:
                pass

            await self.redis.delete("currently_transcoding")
            logger.debug(
                f"Service: Stream {stream_id} transcoding status: {status}")
            return status

    def __set_profiles(self, file_path: str) -> list[dict[str, Any]]:
        video_info = get_video_specs(file_path)
        logger.debug(
            f"Service: Video info for {file_path}: {video_info}")
        profiles_to_use = []
        logger.debug(
            f"Service: Setting profiles for {file_path} with video info: {video_info}")

        if video_info["height"] >= 1080 and video_info["width"] >= 1920:
            if video_info["fps"] == 60:
                profiles_to_use = [
                    self.PROFILES[0], self.PROFILES[3], self.PROFILES[6]]
                logger.debug(
                    f"Service: Using 1080p60 profile for {file_path}")

            elif video_info["fps"] == 50:
                profiles_to_use = [
                    self.PROFILES[1], self.PROFILES[4], self.PROFILES[7]]
                logger.debug(
                    f"Service: Using 1080p50 profile for {file_path}")

            elif video_info["fps"] == 30:
                profiles_to_use = [
                    self.PROFILES[2], self.PROFILES[5], self.PROFILES[6]]
                logger.debug(
                    f"Service: Using 1080p30 profile for {file_path}")

        elif video_info["height"] >= 720 and video_info["width"] >= 1280:
            if video_info["fps"] == 60:
                profiles_to_use = [self.PROFILES[3], self.PROFILES[6]]
                logger.debug(
                    f"Service: Using 720p60 profile for {file_path}")

            elif video_info["fps"] == 50:
                profiles_to_use = [self.PROFILES[4], self.PROFILES[7]]
                logger.debug(
                    f"Service: Using 720p50 profile for {file_path}")

            elif video_info["fps"] == 30:
                profiles_to_use = [self.PROFILES[5], self.PROFILES[6]]
                logger.debug(
                    f"Service: Using 720p30 profile for {file_path}")

        elif video_info["height"] >= 480 and video_info["width"] >= 854:
            if video_info["fps"] in [60, 30]:
                profiles_to_use.append(self.PROFILES[6])

            elif video_info["fps"] in [50, 25]:
                profiles_to_use.append(self.PROFILES[7])
        else:
            logger.debug(
                f"Service: No profiles to use for {file_path} with video info: {video_info}")
            return []

        logger.debug(
            f"Service: Video info for {file_path}: {video_info}, profiles to use: {[profile['name'] for profile in profiles_to_use]}")

        return profiles_to_use

    def __generate_command(self, stream_id: str, type: str = "str"):
        input_file = f"{self.RECORDING_BASE}{stream_id}.mp4"

        try:
            logger.debug(
                f"Service (generate_command): Generating command for stream {stream_id} with input file {input_file}")

            if not os.path.isfile(input_file):
                raise FileNotFoundError

            profiles_to_use = self.__set_profiles(input_file)
            profiles_names = [profile["name"] for profile in profiles_to_use]

            logger.debug(
                f"Service (generate_command): Profiles to use for stream {stream_id}: {profiles_names}")

            if not profiles_to_use:
                raise VideoResolutionFPSException(stream_id)

            output_base = f"{self.HLS_OUTPUT_BASE}{stream_id}"
            profiles_to_use_length = str(len(profiles_to_use))

            command = [
                "ffmpeg", "-loglevel", "debug", "-i", input_file,
                "-filter_complex", f"[0:v]split={profiles_to_use_length}"
            ]

            for profile in profiles_to_use:
                name = profile["name"]
                command[-1] += f"[{name}]"

            for profile in profiles_to_use:
                name = profile["name"]
                scale_width = str(profile["scale_width"])
                scale_height = str(profile["scale_height"])
                fps = str(profile["fps"])

                logger.debug(
                    f"Service (generate_command): Adding filter for {name} profile ({scale_width}x{scale_height}, {fps}fps)")

                command[-1] += f";[{name}]scale=w={scale_width}:h={scale_height}:force_original_aspect_ratio=decrease,fps={fps}"

                if "crop" in profile:
                    command[-1] += f",crop={profile['crop']}"

                command[-1] += f"[{name}_out]"

            for i, profile in enumerate(profiles_to_use):
                name = profile["name"]
                segment_time_in_frames = str(
                    profile["fps"] * self.HLS_SEGMENT_TIME)
                maxbitrate = profile["maxbitrate"]
                hls_segment_time = str(
                    self.HLS_SEGMENT_TIME)
                i_str = str(i)

                command.extend([
                    "-map", f"[{name}_out]",
                    "-map", "0:a",
                    f"-c:v:{i_str}", "libsvtav1",
                    "-crf", "35",
                    "-preset", "10",
                    "-g", f"{segment_time_in_frames}",
                    "-svtav1-params",
                    f"tune=0:fast-decode=2:mbr={maxbitrate}",
                    "-flags", "+cgop"
                ])

            first_profile_name = profiles_to_use[0]["name"]
            command.extend([
                "-c:a", "libopus",
                "-b:a", "160k",
                "-ac", "2",
                "-ar", "48000",
                "-f", "hls",
                "-hls_time", f"{hls_segment_time}",
                "-hls_playlist_type", "vod",
                "-hls_flags", "independent_segments",
                "-master_pl_name", "master.m3u8",
                "-var_stream_map",
                f"v:0,a:0,name:{first_profile_name}"])

            for i, profile in enumerate(profiles_to_use[1:], 1):
                i_str = str(i)
                name = profile["name"]
                command[-1] += f" v:{i_str},a:{i_str},name:{name}"

            command.extend([
                "-hls_segment_type", "fmp4",
                "-hls_segment_filename",
                f"{output_base}/%v/%d.mp4",
                f"{output_base}/%v/stream.m3u8"
            ])

            command_str = " ".join(command)

            logger.debug(
                f"SERVICE: Generated command for stream {stream_id}: {command_str}")

            if type == "list":
                return command

            return command_str
        except Exception as e:
            logger.error(
                f"Service (generate_command): Error generating command for stream {stream_id}: {str(e)}")
            raise e

    async def __generate_thumbnail(self, stream_id: str, fallback: bool = False):
        input_file = f"{self.RECORDING_BASE}{stream_id}.mp4"
        output_file = f"{self.HLS_OUTPUT_BASE}{stream_id}/thumbnail.webp"

        try:
            if not os.path.isfile(input_file):
                raise FileNotFoundError

            command = [
                "ffmpeg", "-loglevel", "debug",
                "-ss", str(time(0, 0, 5)),
                "-i", input_file,
                "-f", "image2",
                "-vf", r"select=(gt(scene\,0.5))" if not fallback else r"select=eq(n\,360)",
                "-frames:v", "1",
                "-fps_mode", "vfr",
                "-c:v", "libwebp",
                "-update", "1",
                output_file
            ]

            logger.debug(
                f"Service: Generating thumbnail for stream {stream_id} with command: {' '.join(command)}")

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.debug(
                    f"Error generating thumbnail for stream {stream_id}: {stderr.decode()}")

            logger.debug(
                f"Service: Thumbnail generated for stream {stream_id} at {output_file}\nstdout:\n{stdout.decode()}\nstderr:\n{stderr.decode()}")

        except Exception as e:
            logger.error(
                f"Service: Error generating thumbnail for stream {stream_id}: {str(e)}")
            raise ThumbnailGenerationException(stream_id, str(e))

    async def stop_queue_processing(self):
        self.can_continue = False

        if self.queue_process:
            await self.queue_process

        self.redis.close()

    async def __notify_stream_status(self, stream_id: str, status: str):
        try:
            async with httpx.AsyncClient() as client:
                await client.patch(f"{self.STREAM_INFO_SERVICE_URL}/streams/{stream_id}/status", json={"status": status})
        except httpx.HTTPStatusError as e:
            raise StreamInfoException(stream_id, e)
