from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.schemas.agent import AgentAskRequest, AgentAskResponse
from backend.app.services.agent import agent_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/ask", response_model=AgentAskResponse)
def ask_assistant(
    payload: AgentAskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return agent_service.ask(
        db,
        user_id=current_user.id,
        question=payload.question,
        resume_id=payload.resume_id,
        job_id=payload.job_id,
    )