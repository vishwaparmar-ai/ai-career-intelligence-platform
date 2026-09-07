import uuid

from sqlalchemy.orm import Session

from backend.app.models.job_profile_model import JobProfile, JobProfileStatus


def get_by_job_id(db: Session, job_id: uuid.UUID) -> JobProfile | None:
    return db.query(JobProfile).filter(JobProfile.job_id == job_id).first()


def upsert_profile(
    db: Session,
    *,
    job_id: uuid.UUID,
    user_id: uuid.UUID,
    status: JobProfileStatus,
    data: dict | None,
    error_message: str | None,
    embedding: list[float] | None = None,
) -> JobProfile:
    existing = get_by_job_id(db, job_id)

    if existing:
        existing.status = status
        existing.data = data
        existing.error_message = error_message
        existing.embedding = embedding
        db.commit()
        db.refresh(existing)
        return existing

    profile = JobProfile(
        job_id=job_id,
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