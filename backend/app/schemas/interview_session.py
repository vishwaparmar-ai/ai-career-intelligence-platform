import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from backend.app.models.interview_session import InterviewSessionStatus


def _normalize_rating(value) -> str:
    """
    Accepts whatever shape the model returns (a string like 'Strong', or a
    number like 4 out of 5) and maps it to one of three fixed labels. The
    numeric bucketing is a rough heuristic, not a precise scale — the goal
    is just to never crash on an unexpected type, the same lesson learned
    from the roadmap's priority field earlier in this project.
    """
    if value is None:
        return "Not assessed"
    if isinstance(value, (int, float)):
        if value >= 4:
            return "Strong"
        if value >= 2.5:
            return "Adequate"
        return "Weak"
    text = str(value).strip()
    return text.capitalize() if text else "Not assessed"


def _normalize_str_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    return value


class QuestionEvaluation(BaseModel):
    # Wire types are deliberately loose (str | float) — Groq's schema
    # validator rejects the whole tool call if the declared type doesn't
    # match what the model sends, so both shapes have to be allowed here
    # before the validator below normalizes to one of three labels.
    technical_accuracy: str | float | None = None
    depth: str | float | None = None
    relevance: str | float | None = None
    strengths: list[str] | str | None = None
    missing_concepts: list[str] | str | None = None
    improvement_advice: str | None = None

    @field_validator("technical_accuracy", "depth", "relevance", mode="before")
    @classmethod
    def _coerce_rating(cls, v):
        return _normalize_rating(v)

    @field_validator("strengths", "missing_concepts", mode="before")
    @classmethod
    def _coerce_list(cls, v):
        return _normalize_str_list(v)


class InterviewQuestionState(BaseModel):
    question: str
    focus_skill: str | None = None
    answer: str | None = None
    answered_at: datetime | None = None
    evaluation: QuestionEvaluation | None = None


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