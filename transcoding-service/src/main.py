# coding=utf-8

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes import transcoding_routes
from src.services.transcoding_service import TranscodingService
from src.controllers.transcoding_controller import set_transcoding_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    transcoding_service = TranscodingService()
    set_transcoding_service(transcoding_service)
    await transcoding_service.start_queue_processing()

    yield

    await transcoding_service.stop_queue_processing()


app = FastAPI(lifespan=lifespan, title="Transcoding Service")

app.include_router(transcoding_routes.router)
