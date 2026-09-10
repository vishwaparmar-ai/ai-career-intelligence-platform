import uuid

from sqlalchemy.orm import Session

from backend.app.models.roadmap_model import Roadmap, RoadmapStatus


def get_by_analysis_id(db: Session, analysis_id: uuid.UUID) -> Roadmap | None:
    return db.query(Roadmap).filter(Roadmap.analysis_id == analysis_id).first()


def upsert_roadmap(
    db: Session,
    *,
    analysis_id: uuid.UUID,
    user_id: uuid.UUID,
    status: RoadmapStatus,
    data: dict | None,
    error_message: str | None,
) -> Roadmap:
    existing = get_by_analysis_id(db, analysis_id)

    if existing:
        existing.status = status
        existing.data = data
        existing.error_message = error_message
        db.commit()
        db.refresh(existing)
        return existing

    roadmap = Roadmap(
        analysis_id=analysis_id,
        user_id=user_id,
        status=status,
        data=data,
        error_message=error_message,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return roadmap