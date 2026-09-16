import uuid

from sqlalchemy.orm import Session

from backend.app.models.interview_session import InterviewSession


def create_session(db: Session, session: InterviewSession) -> InterviewSession:
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session_for_user(
    db: Session, session_id: uuid.UUID, user_id: uuid.UUID
) -> InterviewSession | None:
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.id == session_id, InterviewSession.user_id == user_id)
        .first()
    )


def list_sessions_for_user(db: Session, user_id: uuid.UUID) -> list[InterviewSession]:
    return (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )


def save(db: Session, session: InterviewSession) -> InterviewSession:
    db.commit()
    db.refresh(session)
    return session