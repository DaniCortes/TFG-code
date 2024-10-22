import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.routes import login_routes

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

app.include_router(login_routes.router)

# Configure Tortoise ORM
register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={'models': ['src.models.user_model']},
    generate_schemas=True,
    add_exception_handlers=True,
)
