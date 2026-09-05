import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.repositories import resume_repo
from backend.app.schemas.resume_schema import ResumeRead
from backend.app.services.resume import resume_service

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        resume = resume_service.process_resume_upload(
            db,
            user_id=current_user.id,
            original_filename=file.filename or "resume.pdf",
            content_type=file.content_type,
            file_bytes=file_bytes,
        )
    except resume_service.UnsupportedFileTypeError:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    except resume_service.FileTooLargeError:
        raise HTTPException(
            status_code=400, detail="File is too large — the limit is 5MB."
        )

    return resume


@router.get("", response_model=list[ResumeRead])
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return resume_repo.list_resumes_for_user(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeRead)
def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = resume_repo.get_resume_for_user(db, resume_id, current_user.id)
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume