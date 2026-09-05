import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import candidate_profile_repo
from backend.app.schemas.candidate_schema import CandidateProfileRead
from backend.app.services import candidate_extraction_service

router = APIRouter(prefix="/resumes", tags=["candidate-profile"])


@router.post(
    "/{resume_id}/parse",
    response_model=CandidateProfileRead,
    status_code=status.HTTP_201_CREATED,
)
def parse_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        profile = candidate_extraction_service.parse_resume(
            db, resume_id=resume_id, user_id=current_user.id
        )
    except candidate_extraction_service.ResumeNotReadyError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return profile


@router.get("/{resume_id}/profile", response_model=CandidateProfileRead)
def get_profile(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = candidate_profile_repo.get_by_resume_id(db, resume_id)
    if profile is None or profile.user_id != current_user.id:
        raise HTTPException(
            status_code=404, detail="No profile found for this resume."
        )
    return profile