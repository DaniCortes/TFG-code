import json
import subprocess

from src.utils.logger import logger


def get_video_specs(file_path: str) -> dict:
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams',
        file_path
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        # logger.debug(f"Video info: {video_info}")

        # Find the video stream
        video_stream = next(
            stream for stream in video_info['streams'] if stream['codec_type'] == 'video')

        width = int(video_stream['width'])
        height = int(video_stream['height'])

        # Frame rate must be an integer, so we round it
        frame_rate = int(round(eval(video_stream['r_frame_rate'])))

        logger.debug(f"Width: {width}, Height: {height}, FPS: {frame_rate}")

        return {'width': width, 'height': height, 'fps': frame_rate}

    except subprocess.CalledProcessError as e:
        raise e

    except json.JSONDecodeError as e:
        raise e

    except Exception as e:
        raise e
