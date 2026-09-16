from pydantic import BaseModel


class RAGSource(BaseModel):
    topic: str
    title: str
    similarity: float


class RAGAnswer(BaseModel):
    answer: str
    sources: list[RAGSource]
    # False when no chunk cleared the relevance threshold — the answer in
    # that case is a fixed "I don't have relevant information" message,
    # not something the LLM even got a chance to generate or hallucinate.
    grounded: bool