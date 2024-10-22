from fastapi import FastAPI
from routes import transmuxing_routes


app = FastAPI()

app.include_router(transmuxing_routes.router)
