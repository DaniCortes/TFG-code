from fastapi import FastAPI

from src.routes import transmuxing_routes

app = FastAPI(title="Transmuxing Service")

app.include_router(transmuxing_routes.router)
