import os
from fastapi import FastAPI
from src.routes import stream_routes
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI(title="Stream Information Service")

app.include_router(stream_routes.router)


# PostgreSQL connection
POSTGRES_URL = os.getenv("POSTGRES_URL")

register_tortoise(
    app,
    db_url=POSTGRES_URL,
    modules={'models': ['src.models.user_models']},
    generate_schemas=True,
    add_exception_handlers=True,
)
