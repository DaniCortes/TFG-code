import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.connection import ConnectionHandler
from tortoise.contrib.fastapi import RegisterTortoise

from src.routes import register_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(os.getenv("POSTGRES_URL"))
    async with RegisterTortoise(
        app=app,
        db_url=os.getenv("POSTGRES_URL"),
        modules={"models": ["src.models.user_model"]},
        generate_schemas=True,
        add_exception_handlers=True
    ):
        yield
    await ConnectionHandler().close_all()

app = FastAPI(lifespan=lifespan, title="Register Service")

app.include_router(register_routes.router)
