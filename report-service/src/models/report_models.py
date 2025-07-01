from datetime import datetime, timezone
from typing import Annotated

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
    reporter_id: str
    reported_id: str
    reason: str = Field(pattern=f"^({'|'.join(report_reasons)})$")
    status: str = Field(default="pending", pattern="^(pending|resolved)$")
    reported_type: str = Field(pattern="^(stream|message|user)$")
    outcome: Annotated[str | None, Field(
        pattern="^(resolved|ignored|escalated)$")] = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
