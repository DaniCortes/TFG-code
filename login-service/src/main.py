from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise
from tortoise.connection import ConnectionHandler
from src.routes import login_routes


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

app = FastAPI(lifespan=lifespan, title="Login Service")

app.include_router(login_routes.router)
