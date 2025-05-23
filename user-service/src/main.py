import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.connection import ConnectionHandler
from tortoise.contrib.fastapi import RegisterTortoise

from src.routes import user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with RegisterTortoise(
        app=app,
        db_url=os.getenv("POSTGRES_URL"),
        modules={"models": ["src.models.user_models"]},
        generate_schemas=True,
        add_exception_handlers=True
    ):
        yield
    await ConnectionHandler().close_all()

app = FastAPI(lifespan=lifespan, title="User Service")

app.include_router(user_routes.router)
