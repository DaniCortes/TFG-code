from fastapi import APIRouter
from controllers.stream_info_controller import StreamController
from models.stream_models import Stream, IngestRequest

router = APIRouter()
stream_controller = StreamController()


@router.post("/streams", status_code=201)
async def create_or_terminate_stream(request: IngestRequest):
    call = request.call
    stream_key = request.name

    if call == "play":
        return await stream_controller.create_stream(stream_key)

    else:
        return await stream_controller.transcode_stream(stream_key)


@router.get("/streams/{stream_id}", response_model=Stream)
async def get_stream(stream_id: str):
    return await stream_controller.get_stream(stream_id)


@router.patch("/streams/{stream_id}", status_code=204, response_model=Stream)
async def update_stream(stream_id: str, status: str):
    return await stream_controller.update_stream(stream_id, status)


@router.get("/streams", response_model=list[Stream])
async def list_streams():
    return await stream_controller.list_streams()
