"""
AI Career Intelligence Platform — FastAPI entrypoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.resume import router as resume_router
from backend.app.api.routes.candidate import router as candidate_router
from backend.app.api.routes.jobs import router as job_router
from backend.app.api.routes.skills import router as skill_router

settings = get_settings()

app = FastAPI(title="AI Career Intelligence Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(candidate_router)
app.include_router(job_router)
app.include_router(skill_router)

@app.get("/health")
def health():
    return {"status": "ok"}