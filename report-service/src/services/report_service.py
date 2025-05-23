import os
from typing import List

from pymongo import AsyncMongoClient

from src.models.report_models import Report


class ReportService:

    def __init__(self):
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.mongo_client = AsyncMongoClient(self.MONGO_URL)
        self.database = self.mongo_client.stream_db
        self.collection = self.database.get_collection("reports")

    async def create_report(self, report_data: Report):
        return await self.collection.insert_one(report_data)

    async def get_reports(self, content_range: dict) -> tuple[List[Report], int]:
        reports = []
        async for report in self.collection.find().skip(content_range["start"]).limit(content_range["limit"]):
            report["id"] = str(report["_id"])
            del report["_id"]

            reports.append(Report(**report))

        return reports, await self.__get_reports_total()

    async def update_report(self, report_id: str, report_data: Report):
        return await self.collection.update_one({"id": report_id}, {"$set": report_data.model_dump(exclude_unset=True)})

    async def __get_reports_total(self):
        return await self.collection.count_documents({})
