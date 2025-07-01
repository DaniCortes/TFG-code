from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.routes import transcoding_routes
from src.services.transcoding_service import TranscodingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    transcoding_service = transcoding_routes.transcoding_service
    yield

    await transcoding_service.stop_queue_processing()


app = FastAPI(lifespan=lifespan, title="Transcoding Service")

app.include_router(transcoding_routes.router)
