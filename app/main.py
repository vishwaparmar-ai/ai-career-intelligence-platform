"""
AI Career Intelligence Platform — FastAPI entrypoint.
"""

from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI Career Intelligence Platform",
    description="Resume + job description -> readiness score, skill-gap analysis, roadmap, and interview practice.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}


@app.get("/readiness", tags=["system"])
async def readiness() -> dict:
    return {"status": "ready"}



