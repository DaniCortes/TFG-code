from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.distribution_routes import router as stream_router

app = FastAPI(title="HLS Distribution Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(stream_router)
