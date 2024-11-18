import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.connection import ConnectionHandler
from tortoise.contrib.fastapi import RegisterTortoise

from src.routes import stream_info_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(
        app=app,
        db_url=os.getenv("POSTGRES_URL"),
        modules={"models": ["src.models.user_model"]},
        generate_schemas=True,
        add_exception_handlers=True
    ):
        yield
    await ConnectionHandler().close_all()

app = FastAPI(lifespan=lifespan, title="Stream Information Service")

app.include_router(stream_info_routes.router)
