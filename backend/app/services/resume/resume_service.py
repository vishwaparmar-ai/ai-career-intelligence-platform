import uuid
from io import BytesIO

from pypdf import PdfReader
from sqlalchemy.orm import Session

from backend.app.models.resume_model import Resume, ResumeStatus
from backend.app.repositories import resume_repo

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
ALLOWED_CONTENT_TYPE = "application/pdf"
PDF_MAGIC_BYTES = b"%PDF-"


class UnsupportedFileTypeError(Exception):
    pass


class FileTooLargeError(Exception):
    pass


def _validate_upload(content_type: str | None, file_bytes: bytes) -> None:
    if content_type != ALLOWED_CONTENT_TYPE:
        raise UnsupportedFileTypeError()

    # The Content-Type header is client-supplied and easy to spoof, so this
    # is treated as untrusted data — check the actual file signature too.
    if not file_bytes.startswith(PDF_MAGIC_BYTES):
        raise UnsupportedFileTypeError()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError()


def _extract_text(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))

    if reader.is_encrypted:
        raise ValueError("This PDF is password-protected.")

    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()


def process_resume_upload(
    db: Session,
    *,
    user_id: uuid.UUID,
    original_filename: str,
    content_type: str | None,
    file_bytes: bytes,
) -> Resume:
    # Type/size checks raise — the route turns these into 400s, since
    # they're the user's mistake, not a processing failure worth a DB row.
    _validate_upload(content_type, file_bytes)

    error_message: str | None = None
    text: str | None = None

    try:
        text = _extract_text(file_bytes)
        if not text:
            error_message = (
                "No extractable text found — this looks like a scanned "
                "or image-only PDF."
            )
            text = None
    except ValueError as exc:
        # Known, explainable failure (e.g. password-protected).
        error_message = str(exc)
    except Exception:
        # Corrupted or malformed PDF. Deliberately vague to the user and
        # never includes the raw exception — could leak internals, and we
        # never log resume content anyway per the project's security rules.
        error_message = "Couldn't read this PDF — it may be corrupted."

    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        file_size_bytes=len(file_bytes),
        status=ResumeStatus.failed if error_message else ResumeStatus.ready,
        raw_text=text,
        char_count=len(text) if text else None,
        error_message=error_message,
    )
    return resume_repo.create_resume(db, resume)