from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.knowledge_chunk_model import KnowledgeChunk


def create_chunk(db: Session, chunk: KnowledgeChunk) -> KnowledgeChunk:
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def count_chunks(db: Session) -> int:
    return db.query(KnowledgeChunk).count()


def search_similar(
    db: Session, query_embedding: list[float], limit: int = 5
) -> list[tuple[KnowledgeChunk, float]]:
    """
    Real pgvector similarity search in Postgres — same cosine_distance
    pattern as the candidate/job matching from Day 17, applied here to
    find the closest knowledge chunks to a query instead of comparing two
    specific profiles. Returns (chunk, similarity) pairs, best match first.
    """
    distance_col = KnowledgeChunk.embedding.cosine_distance(query_embedding).label(
        "distance"
    )
    rows = db.execute(
        select(KnowledgeChunk, distance_col).order_by(distance_col).limit(limit)
    ).all()
    return [(row[0], 1.0 - row[1]) for row in rows]