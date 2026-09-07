import uuid

from sqlalchemy.orm import Session

from backend.app.models.analysis_model import Analysis


def create_analysis(db: Session, analysis: Analysis) -> Analysis:
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def list_analyses_for_user(db: Session, user_id: uuid.UUID) -> list[Analysis]:
    return (
        db.query(Analysis)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )


def get_analysis_for_user(
    db: Session, analysis_id: uuid.UUID, user_id: uuid.UUID
) -> Analysis | None:
    return (
        db.query(Analysis)
        .filter(Analysis.id == analysis_id, Analysis.user_id == user_id)
        .first()
    )