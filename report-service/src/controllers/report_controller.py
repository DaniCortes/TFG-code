import re
from typing import List, Tuple

from fastapi import HTTPException

from src.models.report_models import Report
from src.models.user_model import User
from src.services.report_service import ReportService


class ReportController:
    def __init__(self, service: ReportService):
        self.service = service

    async def create_report(self, report_data: Report, current_user: User) -> Report:
        report_data.reporter_user_id = current_user.id
        return await self.service.create_report(report_data)

    async def get_reports(self, status: str, current_user: User, content_range_str: str) -> Tuple[List[Report], List[str]]:
        if current_user.is_admin:

            match = re.match(r"(\w+)=(\d+)-(\d+)", content_range_str)
            if not match:
                raise HTTPException(
                    status_code=400, detail="Invalid Range header: wrong format, expected format: item=start-end")

            if match.group(1) != "reports":
                raise HTTPException(
                    status_code=400, detail="Invalid Range header: wrong item")

            content_range = {
                "item": match.group(1),
                "start": int(match.group(2)),
                "end": int(match.group(3)),
                "limit": int(match.group(3)) - int(match.group(2)) + 1,
            }

            if content_range["start"] > content_range["end"]:
                raise HTTPException(
                    status_code=400, detail="Invalid Range header: start cannot be greater than end")

            reports, total_reports = await self.service.get_reports(status, content_range)

            accept_ranges_header = f"Accept-Ranges: {content_range['item']}"
            content_range_header = f"Content-Range: {content_range['item']} {content_range['start']}-{content_range['end']}/{total_reports}"

            headers = [accept_ranges_header, content_range_header]

            return reports, headers

        else:
            raise HTTPException(
                status_code=403, detail="You are not authorized to access this resource.")

    async def update_report(self, report_id: str, report_data: Report, current_user: User) -> Report:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=403, detail="You are not authorized to update this report.")

        return await self.service.update_report(report_id, report_data, current_user)
