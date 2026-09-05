import uuid

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
) -> CandidateProfile:
    existing = get_by_resume_id(db, resume_id)

    if existing:
        existing.status = status
        existing.data = data
        existing.error_message = error_message
        db.commit()
        db.refresh(existing)
        return existing

    profile = CandidateProfile(
        resume_id=resume_id,
        user_id=user_id,
        status=status,
        data=data,
        error_message=error_message,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile