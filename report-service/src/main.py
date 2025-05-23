from fastapi import FastAPI

from src.routes.report_routes import router as report_router

app = FastAPI(title="Report Service")

app.include_router(report_router)
