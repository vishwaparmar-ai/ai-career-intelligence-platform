import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import job_profile_repo, job_repo
from backend.app.schemas.job_schema import JobCreate, JobProfileRead, JobRead
from backend.app.services.job import job_extraction_service,job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return job_service.create_job(db, user_id=current_user.id, payload=payload)


@router.get("", response_model=list[JobRead])
def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return job_repo.list_jobs_for_user(db, current_user.id)


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = job_repo.get_job_for_user(db, job_id, current_user.id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.post(
    "/{job_id}/parse",
    response_model=JobProfileRead,
    status_code=status.HTTP_201_CREATED,
)
def parse_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        profile = job_extraction_service.parse_job(
            db, job_id=job_id, user_id=current_user.id
        )
    except job_extraction_service.JobNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return profile


@router.get("/{job_id}/profile", response_model=JobProfileRead)
def get_job_profile(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = job_profile_repo.get_by_job_id(db, job_id)
    if profile is None or profile.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="No profile found for this job.")
    return profile