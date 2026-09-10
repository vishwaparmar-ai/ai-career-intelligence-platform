from sqlalchemy.orm import Session

from backend.app.models.knowledge_chunk_model import KnowledgeChunk
from backend.app.repositories import knowledge_repo
from backend.app.services.rag import embedding_service


def ingest_chunk(
    db: Session, *, topic: str, title: str, content: str, chunk_index: int
) -> KnowledgeChunk:
    embedding = embedding_service.embed_text(content)
    chunk = KnowledgeChunk(
        topic=topic,
        title=title,
        content=content,
        chunk_index=chunk_index,
        embedding=embedding,
    )
    return knowledge_repo.create_chunk(db, chunk)


def search(
    db: Session, query: str, limit: int = 5
) -> list[tuple[KnowledgeChunk, float]]:
    query_embedding = embedding_service.embed_text(query)
    return knowledge_repo.search_similar(db, query_embedding, limit=limit)