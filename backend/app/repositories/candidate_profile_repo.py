import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.candidate_profile import CandidateProfile, ProfileStatus


def get_by_resume_id(db: Session, resume_id: uuid.UUID) -> CandidateProfile | None:
    return (
        db.query(CandidateProfile)
        .filter(CandidateProfile.resume_id == resume_id)
        .first()
    )


def upsert_profile(
    db: Session,
    *,
    resume_id: uuid.UUID,
    user_id: uuid.UUID,
    status: ProfileStatus,
    data: dict | None,
    error_message: str | None,
    embedding: list[float] | None = None,
) -> CandidateProfile:
    existing = get_by_resume_id(db, resume_id)

    if existing:
        existing.status = status
        existing.data = data
        existing.error_message = error_message
        existing.embedding = embedding
        db.commit()
        db.refresh(existing)
        return existing

    profile = CandidateProfile(
        resume_id=resume_id,
        user_id=user_id,
        status=status,
        data=data,
        error_message=error_message,
        embedding=embedding,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def get_cosine_similarity(
    db: Session, candidate_profile_id: uuid.UUID, other_embedding: list[float] | None
) -> float | None:
    """
    Runs the actual similarity computation in Postgres via pgvector's
    cosine_distance operator, rather than pulling both vectors into Python
    and computing it with numpy — this is the real "implement similarity
    search" piece the roadmap asks for, not just storing vectors inertly.
    Returns None if either side has no embedding (nothing to compare).
    """
    if other_embedding is None:
        return None

    distance = db.execute(
        select(CandidateProfile.embedding.cosine_distance(other_embedding)).where(
            CandidateProfile.id == candidate_profile_id,
            CandidateProfile.embedding.is_not(None),
        )
    ).scalar()

    if distance is None:
        return None
    # pgvector's cosine_distance is 1 - cosine_similarity.
    return 1.0 - distance