from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import skill_repo
from backend.app.services.matching import skill_taxonomy

router = APIRouter(prefix="/skills", tags=["skills"])


class NormalizeRequest(BaseModel):
    skills: list[str]


class NormalizeResponse(BaseModel):
    normalized: list[str]


@router.post("/normalize", response_model=NormalizeResponse)
def normalize_skills(
    payload: NormalizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NormalizeResponse(
        normalized=skill_taxonomy.normalize_skills(db, payload.skills)
    )


@router.get("")
def list_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [{"id": str(s.id), "name": s.name} for s in skill_repo.list_skills(db)]