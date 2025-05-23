from datetime import datetime, timezone

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

report_reasons = {
    "Spam",
    "Inappropriate",
    "Hate speech",
    "Violence",
    "Harassment",
    "False information",
    "Self harm",
    "Nudity",
    "Terrorism",
    "Other",
}


class Report(BaseModel):
    id: str | None = None
    reported_user_id: str
    content_id: str
    reason: str
    status: str = Field(default="pending")
    content_type: str
    outcome: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("reason", mode="before")
    @classmethod
    def validate_reason(cls, value):
        if value not in report_reasons:
            raise HTTPException(
                status_code=400, detail=f"Invalid report reason: {value}. Must be one of these: {', '.join(report_reasons)}")
        return value

    @field_validator("content_type", mode="before")
    @classmethod
    def validate_content_type(cls, value):
        if value not in {"stream", "message"}:
            raise HTTPException(
                status_code=400, detail="Content type must be either 'stream' or 'message'")
        return value

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value):
        if value not in {"pending", "resolved"}:
            raise HTTPException(
                status_code=400, detail="Report status must be either 'pending' or 'resolved'")
        return value
