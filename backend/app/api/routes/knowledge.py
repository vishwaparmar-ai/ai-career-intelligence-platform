from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import knowledge_repo
from backend.app.services.rag import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/search")
def search_knowledge(
    q: str = Query(..., min_length=3),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = knowledge_service.search(db, q, limit=limit)
    return [
        {
            "topic": chunk.topic,
            "title": chunk.title,
            "content": chunk.content,
            "similarity": round(similarity, 4),
        }
        for chunk, similarity in results
    ]


@router.get("/count")
def count_knowledge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return {"chunk_count": knowledge_repo.count_chunks(db)}