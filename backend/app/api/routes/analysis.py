import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import analysis_repo
from backend.app.schemas.analysis_schema import AnalysisRead, MatchResult
from backend.app.services.matching import analysis_service

router = APIRouter(prefix="/analyses", tags=["analyses"])


class RunAnalysisRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


def _to_read(analysis) -> AnalysisRead:
    # Built explicitly rather than via from_attributes — result_data is
    # stored as a plain JSONB dict, so it's parsed back into the typed
    # MatchResult here rather than relying on Pydantic to reach into a
    # differently-named ORM column.
    return AnalysisRead(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_id=analysis.job_id,
        overall_score=analysis.overall_score,
        result=MatchResult(**analysis.result_data),
        created_at=analysis.created_at,
    )


@router.post("", response_model=AnalysisRead, status_code=status.HTTP_201_CREATED)
def run_analysis(
    payload: RunAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        analysis = analysis_service.run_analysis(
            db,
            user_id=current_user.id,
            resume_id=payload.resume_id,
            job_id=payload.job_id,
        )
    except analysis_service.AnalysisNotPossibleError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _to_read(analysis)


@router.get("", response_model=list[AnalysisRead])
def list_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [
        _to_read(a) for a in analysis_repo.list_analyses_for_user(db, current_user.id)
    ]


@router.get("/{analysis_id}", response_model=AnalysisRead)
def get_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    analysis = analysis_repo.get_analysis_for_user(
        db, analysis_id, current_user.id
    )
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _to_read(analysis)