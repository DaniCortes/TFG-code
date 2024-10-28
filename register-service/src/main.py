import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.routes import register_routes

app = FastAPI(title="Register Service")

app.include_router(register_routes.router)

POSTGRES_URL = os.getenv("POSTGRES_URL")

register_tortoise(
    app,
    db_url=POSTGRES_URL,
    modules={'models': ['src.models.user_model']},
    generate_schemas=True,
    add_exception_handlers=True,
)
