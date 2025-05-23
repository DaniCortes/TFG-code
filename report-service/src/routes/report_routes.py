from typing import List

from fastapi import APIRouter, Depends, Header, Response
from fastapi.responses import JSONResponse

from src.controllers.report_controller import ReportController
from src.models.report_models import Report
from src.models.user_model import User
from src.services.report_service import ReportService
from src.utils.token_utils import get_current_user

router = APIRouter()
service = ReportService()
controller = ReportController(service)


@router.post("/report", status_code=201)
async def report(report_data: Report):
    await controller.create_report(report_data)


@router.get("/reports", response_model=List[Report], status_code=206)
async def get_reports(response: Response, current_user: User = Depends(get_current_user), range: str = Header(...)):
    reports, headers = await controller.get_reports(current_user, range)
    for header in headers:
        response.headers[header.split(":")[0]] = header.split(":")[1].strip()

    return reports
# https://otac0n.com/blog/2012/11/21/range-header-i-choose-you.html


@router.put("/report/{report_id}", status_code=200)
async def update_report_status(report_id: str, report_data: Report):
    return await controller.update_report(report_id, report_data)
