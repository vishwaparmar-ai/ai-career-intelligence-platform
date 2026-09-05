from pydantic import BaseModel, Field

from backend.app.models.candidate_profile import ProfileStatus


class ExperienceEntry(BaseModel):
    title: str
    company: str
    start_date: str | None = Field(
        None, description="As written in the resume, e.g. 'Jan 2022' or '2022'"
    )
    end_date: str | None = Field(
        None, description="As written in the resume, e.g. 'Mar 2024' or 'Present'"
    )
    description: str | None = Field(
        None, description="Key responsibilities or achievements, summarized"
    )


class EducationEntry(BaseModel):
    degree: str
    institution: str
    start_date: str | None = None
    end_date: str | None = None


class ProjectEntry(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class CertificationEntry(BaseModel):
    name: str
    issuer: str | None = None
    date: str | None = None


class CandidateProfileData(BaseModel):
    """
    This is the exact shape we ask the LLM to fill in via tool use, and the
    exact shape we validate its output against before persisting anything.
    """

    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)


class CandidateProfileRead(BaseModel):
    status: ProfileStatus
    data: CandidateProfileData | None
    error_message: str | None

    model_config = {"from_attributes": True}