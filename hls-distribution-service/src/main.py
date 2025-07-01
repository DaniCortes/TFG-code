from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes.live_routes import router as live_router
from src.routes.vod_routes import router as vod_router

app = FastAPI(title="HLS Distribution Service")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(live_router)
app.include_router(vod_router)
