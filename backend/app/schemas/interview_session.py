import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.app.models.interview_session import InterviewSessionStatus


class InterviewQuestionState(BaseModel):
    question: str
    focus_skill: str | None = None
    answer: str | None = None
    answered_at: datetime | None = None


class InterviewSessionRead(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    status: InterviewSessionStatus
    questions: list[InterviewQuestionState]
    current_index: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmitAnswerRequest(BaseModel):
    answer: str