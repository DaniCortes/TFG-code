from fastapi import FastAPI

from src.routes import chat_routes

app = FastAPI(title="Chat Service")

app.include_router(chat_routes.router)
