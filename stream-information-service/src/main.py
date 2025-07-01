from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import stream_info_routes

app = FastAPI(title="Stream Information Service")

origins = [
    "https://localhost:8100",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stream_info_routes.router)
