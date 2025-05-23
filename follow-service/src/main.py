from fastapi import FastAPI

from src.routes import follow_routes

app = FastAPI(title="Follow Service")

app.include_router(follow_routes.router)
