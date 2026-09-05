import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.app.models.resume_model import ResumeStatus


class ResumeRead(BaseModel):
    id: uuid.UUID
    original_filename: str
    status: ResumeStatus
    char_count: int | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}