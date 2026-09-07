"""
Local embedding generation via fastembed — no API key, no rate limits, no
network call at inference time. This is deliberately separate from
services/llm/client.py: embeddings and chat completions are different
capabilities, and Groq specifically does not offer an embeddings endpoint
at all, so this can't go through the same provider abstraction.

Model is loaded once per process (not per-request) since fastembed loads
ONNX weights into memory — the first call after the server starts will be
slower while it initializes.
"""

from fastembed import TextEmbedding

from backend.app.models.candidate_profile import EMBEDDING_DIM
from backend.app.schemas.candidate_schema import CandidateProfileData
from backend.app.schemas.job_schema import JobProfileData

_MODEL_NAME = "BAAI/bge-small-en-v1.5"  # 384 dimensions — must match EMBEDDING_DIM
_model = TextEmbedding(model_name=_MODEL_NAME)


def embed_text(text: str) -> list[float]:
    text = text.strip()
    if not text:
        # A zero vector is a safe, valid embedding — it'll just have
        # ~0 cosine similarity with everything, which is the correct
        # behavior for "there was nothing to embed."
        return [0.0] * EMBEDDING_DIM
    vector = next(_model.embed([text]))
    return vector.tolist()


def candidate_profile_to_text(data: CandidateProfileData) -> str:
    """
    Builds a plain-text summary of the candidate's capabilities for
    embedding — skills plus what they actually did, not just a keyword
    dump, so semantic similarity can pick up on described responsibilities
    that don't literally match a job's wording.
    """
    parts: list[str] = []

    if data.skills:
        parts.append("Skills: " + ", ".join(data.skills))

    for exp in data.experience:
        header = f"{exp.title or ''} at {exp.company or ''}".strip()
        body = " ".join(exp.description)
        if header or body:
            parts.append(f"{header}: {body}".strip(": "))

    for proj in data.projects:
        body = " ".join(proj.description)
        tech = ", ".join(proj.technologies)
        line = f"Project {proj.name}: {body}"
        if tech:
            line += f" Technologies: {tech}"
        parts.append(line)

    return "\n".join(p for p in parts if p.strip())


def job_profile_to_text(data: JobProfileData) -> str:
    parts: list[str] = []

    if data.required_skills:
        parts.append("Required skills: " + ", ".join(data.required_skills))
    if data.preferred_skills:
        parts.append("Preferred skills: " + ", ".join(data.preferred_skills))
    if data.seniority:
        parts.append("Seniority: " + data.seniority)
    if data.responsibilities:
        parts.append("Responsibilities: " + " ".join(data.responsibilities))
    if data.education_requirements:
        parts.append("Education: " + " ".join(data.education_requirements))

    return "\n".join(p for p in parts if p.strip())