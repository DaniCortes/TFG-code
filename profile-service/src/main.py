from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from tortoise.connection import ConnectionHandler
from tortoise.contrib.fastapi import RegisterTortoise
from src.routes.profile_routes import router as profile_router


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

app = FastAPI(lifespan=lifespan, title="Profile Edit Service")

app.include_router(profile_router)
