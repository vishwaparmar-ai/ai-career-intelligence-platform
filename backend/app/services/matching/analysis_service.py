import uuid

from sqlalchemy.orm import Session

from backend.app.models.analysis_model import Analysis
from backend.app.models.candidate_profile import ProfileStatus
from backend.app.models.job_profile_model import JobProfileStatus
from backend.app.repositories import (
    analysis_repo,
    candidate_profile_repo,
    job_profile_repo,
    job_repo,
    resume_repo,
)
from backend.app.schemas.candidate_schema import CandidateProfileData
from backend.app.schemas.job_schema import JobProfileData
from backend.app.services.matching import gap_analysis_service, matching_service


class AnalysisNotPossibleError(Exception):
    pass


def run_analysis(
    db: Session, *, user_id: uuid.UUID, resume_id: uuid.UUID, job_id: uuid.UUID
) -> Analysis:
    resume = resume_repo.get_resume_for_user(db, resume_id, user_id)
    if resume is None:
        raise AnalysisNotPossibleError("Resume not found.")

    job = job_repo.get_job_for_user(db, job_id, user_id)
    if job is None:
        raise AnalysisNotPossibleError("Job not found.")

    candidate_profile = candidate_profile_repo.get_by_resume_id(db, resume_id)
    if candidate_profile is None or candidate_profile.status != ProfileStatus.ready:
        raise AnalysisNotPossibleError(
            "Extract this resume's profile first (on the Resume tab)."
        )

    job_profile = job_profile_repo.get_by_job_id(db, job_id)
    if job_profile is None or job_profile.status != JobProfileStatus.ready:
        raise AnalysisNotPossibleError(
            "Extract this job's requirements first (on the Job tab)."
        )

    candidate_data = CandidateProfileData(**candidate_profile.data)
    job_data = JobProfileData(**job_profile.data)

    # Real pgvector cosine similarity, computed in Postgres — falls back
    # to 0.0 (not an error) if either profile predates the embedding
    # column, e.g. was parsed before this feature existed.
    similarity = candidate_profile_repo.get_cosine_similarity(
        db, candidate_profile.id, job_profile.embedding
    )
    semantic_score = max(0.0, min(1.0, similarity)) if similarity is not None else 0.0

    result = matching_service.compute_match(
        db, candidate_data, job_data, semantic_score=semantic_score
    )
    gap_analysis = gap_analysis_service.compute_gap_analysis(db, candidate_data, job_data)

    analysis = Analysis(
        user_id=user_id,
        resume_id=resume_id,
        job_id=job_id,
        overall_score=result.overall_score,
        result_data=result.model_dump(mode="json"),
        gap_analysis_data=gap_analysis.model_dump(mode="json"),
    )
    return analysis_repo.create_analysis(db, analysis)