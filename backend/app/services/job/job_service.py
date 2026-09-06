import uuid

from sqlalchemy.orm import Session

from backend.app.models.job_model import Job
from backend.app.repositories import job_repo
from backend.app.schemas.job_schema import JobCreate


def create_job(db: Session, *, user_id: uuid.UUID, payload: JobCreate) -> Job:
    job = Job(
        user_id=user_id,
        title=payload.title,
        company=payload.company,
        raw_text=payload.raw_text,
    )
    return job_repo.create_job(db, job)