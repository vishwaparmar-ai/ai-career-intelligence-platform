import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.app.schemas.gap_analysis_schema import GapAnalysis


class SkillMatchDetail(BaseModel):
    matched: list[str]
    missing: list[str]
    score: float  # 0.0-1.0


class ExperienceMatchDetail(BaseModel):
    candidate_years: float
    required_years: float | None
    score: float


class ProjectMatchDetail(BaseModel):
    matched_skills: list[str]
    score: float


class EducationMatchDetail(BaseModel):
    candidate_level: str | None
    required_level: str | None
    score: float


class MatchResult(BaseModel):
    overall_score: float  # 0-100
    required_skills: SkillMatchDetail
    preferred_skills: SkillMatchDetail
    experience: ExperienceMatchDetail
    projects: ProjectMatchDetail
    education: EducationMatchDetail
    semantic_score: float
    weights: dict[str, float]


class AnalysisRead(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    overall_score: float
    result: MatchResult
    gap_analysis: GapAnalysis
    created_at: datetime

    model_config = {"from_attributes": True}