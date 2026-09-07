import enum
import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base

# fastembed's BAAI/bge-small-en-v1.5 produces 384-dimensional vectors —
# this must match services/embedding_service.py's model choice exactly,
# or pgvector will reject inserts with a dimension mismatch.
EMBEDDING_DIM = 384


class ProfileStatus(str, enum.Enum):
    ready = "ready"
    failed = "failed"


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # unique=True: one profile per resume — re-parsing updates this row
    # in place rather than accumulating duplicates.
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[ProfileStatus] = mapped_column(
        Enum(ProfileStatus, name="profile_status"), nullable=False
    )
    data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Nullable: rows parsed before this column existed, or failed
    # extractions, simply have no embedding — matching_service treats a
    # missing embedding as semantic_score=0.0, never an error.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )