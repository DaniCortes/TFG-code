from subprocess import SubprocessError
from fastapi import HTTPException
from src.services.transmuxing_service import TransmuxingService
from src.models.stream_models import StreamResponse, StreamRequest
from src.utils.exceptions import StreamNotFoundException


class TransmuxingController:
    def __init__(self):
        self.transmuxing_service = TransmuxingService()

    async def start_stream(self, request: StreamRequest):
        empty_params = [param for param, value in request.model_dump(
        ).items() if value is None or value == ""]

        if empty_params:
            raise HTTPException(
                status_code=400, detail=f"The following parameters cannot be empty: {', '.join(empty_params)}")

        try:
            stream_id = await self.transmuxing_service.start_transmuxing(request)

        except ValueError as ve:
            raise HTTPException(
                status_code=400, detail="Invalid stream key: " + str(ve))

        except OSError as e:
            raise HTTPException(
                status_code=500, detail="File system error: " + str(e))

        except SubprocessError as e:
            raise HTTPException(
                status_code=500, detail="Failed to start streaming process: " + str(e))

        except Exception as e:
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred: " + str(e))

        if not stream_id:
            raise HTTPException(
                status_code=500, detail="Failed to start stream")
        return StreamResponse(id=stream_id, status="live")

    async def stop_stream(self, stream_id: str):
        try:
            return await self.transmuxing_service.stop_transmuxing(stream_id)

        except StreamNotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))

        except SubprocessError as e:
            raise HTTPException(
                status_code=500, detail="Failed to stop streaming process: " + str(e))

        except Exception as e:
            raise HTTPException(
                status_code=500, detail="An unexpected error occurred: " + str(e))
