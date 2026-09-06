import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from backend.app.models.job_profile_model import JobProfileStatus


class JobCreate(BaseModel):
    title: str | None = Field(None, max_length=255)
    company: str | None = Field(None, max_length=255)
    # min_length guards against parsing a one-line paste-mistake and
    # wasting an LLM call on it; max_length keeps a single request bounded.
    raw_text: str = Field(min_length=50, max_length=20000)


class JobRead(BaseModel):
    id: uuid.UUID
    title: str | None
    company: str | None
    raw_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class JobProfileData(BaseModel):
    """The exact shape the LLM fills in via tool use, and what we validate its output against."""

    # Every list field here is `| None` at the type level specifically so
    # the *wire* JSON schema (what Groq validates the tool call against)
    # accepts `null` as well as an array. gpt-oss-20b sometimes returns
    # `null` for a section it found nothing for, instead of `[]` — without
    # this, Groq's own schema validator rejects the whole tool call with a
    # 400 before our code ever sees the response. The field_validator below
    # then normalizes None back to [] immediately, so every other piece of
    # code that touches this model can keep assuming a real list.
    required_skills: list[str] | None = Field(default_factory=list)
    preferred_skills: list[str] | None = Field(default_factory=list)
    min_years_experience: int | None = Field(
        None, description="Minimum years of experience required, if explicitly stated"
    )
    seniority: str | None = Field(
        None,
        description="e.g. 'Entry-level', 'Mid-level', 'Senior', 'Staff' — as implied by the posting",
    )
    responsibilities: list[str] | None = Field(default_factory=list)
    education_requirements: list[str] | None = Field(default_factory=list)

    @field_validator(
        "required_skills",
        "preferred_skills",
        "responsibilities",
        "education_requirements",
        mode="before",
    )
    @classmethod
    def _none_to_empty_list(cls, v):
        return v if v is not None else []


class JobProfileRead(BaseModel):
    status: JobProfileStatus
    data: JobProfileData | None
    error_message: str | None

    model_config = {"from_attributes": True}