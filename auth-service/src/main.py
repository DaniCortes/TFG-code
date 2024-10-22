from fastapi import FastAPI
from src.routes import auth_routes

app = FastAPI()

app.include_router(auth_routes.router)
