from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import follow_routes

app = FastAPI(title="Follow Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(follow_routes.router)
