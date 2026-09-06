import uuid

from sqlalchemy.orm import Session

from backend.app.models.job_model import Job


def create_job(db: Session, job: Job) -> Job:
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs_for_user(db: Session, user_id: uuid.UUID) -> list[Job]:
    return (
        db.query(Job)
        .filter(Job.user_id == user_id)
        .order_by(Job.created_at.desc())
        .all()
    )


def get_job_for_user(db: Session, job_id: uuid.UUID, user_id: uuid.UUID) -> Job | None:
    return db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()