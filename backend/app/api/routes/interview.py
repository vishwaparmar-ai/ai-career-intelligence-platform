import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.schemas.interview_session import InterviewSessionRead, SubmitAnswerRequest
from backend.app.services.interview import interview_service

router = APIRouter(prefix="/interview-sessions", tags=["interview"])


class StartSessionRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID
    count: int | None = None


@router.post("", response_model=InterviewSessionRead, status_code=status.HTTP_201_CREATED)
def start_session(
    payload: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        session = interview_service.start_session(
            db,
            user_id=current_user.id,
            resume_id=payload.resume_id,
            job_id=payload.job_id,
            count=payload.count or interview_service.DEFAULT_QUESTION_COUNT,
        )
    except interview_service.InterviewNotPossibleError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return session


@router.get("/{session_id}", response_model=InterviewSessionRead)
def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return interview_service.get_session(
            db, session_id=session_id, user_id=current_user.id
        )
    except interview_service.InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/{session_id}/answer", response_model=InterviewSessionRead)
def submit_answer(
    session_id: uuid.UUID,
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return interview_service.submit_answer(
            db, session_id=session_id, user_id=current_user.id, answer=payload.answer
        )
    except interview_service.InterviewSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except interview_service.InterviewSessionCompleteError as exc:
        raise HTTPException(status_code=400, detail=str(exc))