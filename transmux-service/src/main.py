from fastapi import FastAPI
from routes import transmuxing_routes


app = FastAPI("Transmuxing Service")

app.include_router(transmuxing_routes.router)
