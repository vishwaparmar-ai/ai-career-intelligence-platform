import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import roadmap_repo
from backend.app.schemas.roadmap_schema import RoadmapRead
from backend.app.services.roadmap import roadmap_service

router = APIRouter(prefix="/analyses", tags=["roadmap"])


@router.post(
    "/{analysis_id}/roadmap",
    response_model=RoadmapRead,
    status_code=status.HTTP_201_CREATED,
)
def generate_roadmap(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        roadmap = roadmap_service.generate_roadmap(
            db, user_id=current_user.id, analysis_id=analysis_id
        )
    except roadmap_service.AnalysisNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return roadmap


@router.get("/{analysis_id}/roadmap", response_model=RoadmapRead)
def get_roadmap(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = roadmap_repo.get_by_analysis_id(db, analysis_id)
    if roadmap is None or roadmap.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="No roadmap found for this analysis.")
    return roadmap