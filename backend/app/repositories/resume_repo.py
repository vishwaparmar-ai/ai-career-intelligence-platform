import uuid

from sqlalchemy.orm import Session

from backend.app.models.resume_model import Resume


def create_resume(db: Session, resume: Resume) -> Resume:
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_resumes_for_user(db: Session, user_id: uuid.UUID) -> list[Resume]:
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )


def get_resume_for_user(
    db: Session, resume_id: uuid.UUID, user_id: uuid.UUID
) -> Resume | None:
    # Filtering by user_id here (not just resume_id) is what stops one user
    # from reading another user's resume by guessing/incrementing an id.
    return (
        db.query(Resume)
        .filter(Resume.id == resume_id, Resume.user_id == user_id)
        .first()
    )