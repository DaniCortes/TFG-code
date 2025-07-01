from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import auth_routes

app = FastAPI(title="Authentication Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
