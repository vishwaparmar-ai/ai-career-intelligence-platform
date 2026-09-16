import uuid

from sqlalchemy.orm import Session

from backend.app.models.candidate_profile import ProfileStatus
from backend.app.models.job_profile_model import JobProfileStatus
from backend.app.models.roadmap_model import RoadmapStatus
from backend.app.repositories import (
    analysis_repo,
    candidate_profile_repo,
    job_profile_repo,
    roadmap_repo,
)
from backend.app.schemas.candidate_schema import CandidateProfileData
from backend.app.schemas.job_schema import JobProfileData
from backend.app.services.interview import interview_service
from backend.app.services.rag import knowledge_service




TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_candidate_profile",
            "description": (
                "Get the structured candidate profile (skills, experience, "
                "education, projects, certifications) for the resume "
                "currently being discussed."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_job_requirements",
            "description": (
                "Look up the job's raw structured requirements "
                "(required/preferred skills, seniority, responsibilities, "
                "education) for the job currently being discussed. Use "
                "this to answer questions ABOUT what the job requires — "
                "never to generate other content like interview questions "
                "yourself (use generate_interview_questions for that)."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_skill_gaps",
            "description": (
                "Get the prioritized matched/partial/missing skill gaps "
                "between the candidate and the job currently being "
                "discussed."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search a small curated knowledge base covering Python, "
                "FastAPI, Docker, AWS, RAG, embeddings, LLMs, PostgreSQL, "
                "Git, and system design for content relevant to a query."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_roadmap",
            "description": (
                "Get the previously generated 30-day learning roadmap for "
                "the candidate/job currently being discussed, if one "
                "exists. Does not generate a new one."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_interview_questions",
            "description": (
                "Use this whenever the user asks for interview questions, "
                "mock interview practice, or what they might be asked in "
                "an interview for the job currently being discussed. "
                "Always prefer this over writing questions yourself from "
                "get_job_requirements — it also factors in the "
                "candidate's specific background and gaps, which a job-"
                "requirements lookup alone does not."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "How many questions to generate",
                    }
                },
            },
        },
    },
]


def execute_tool(
    db: Session,
    *,
    name: str,
    arguments: dict,
    user_id: uuid.UUID,
    resume_id: uuid.UUID | None,
    job_id: uuid.UUID | None,
) -> dict:
    if name == "get_candidate_profile":
        if resume_id is None:
            return {"error": "No resume is currently selected."}
        profile = candidate_profile_repo.get_by_resume_id(db, resume_id)
        if profile is None or profile.user_id != user_id:
            return {"error": "Resume profile not found."}
        if profile.status != ProfileStatus.ready:
            return {"error": "This resume hasn't been parsed yet."}
        return profile.data

    if name == "get_job_requirements":
        if job_id is None:
            return {"error": "No job is currently selected."}
        job_profile = job_profile_repo.get_by_job_id(db, job_id)
        if job_profile is None or job_profile.user_id != user_id:
            return {"error": "Job profile not found."}
        if job_profile.status != JobProfileStatus.ready:
            return {"error": "This job hasn't been parsed yet."}
        return job_profile.data

    if name == "get_skill_gaps":
        if resume_id is None or job_id is None:
            return {"error": "Both a resume and a job need to be selected."}
        analysis = analysis_repo.get_latest_for_pair(
            db, user_id, resume_id, job_id
        )
        if analysis is None:
            return {
                "error": "No readiness analysis has been run for this resume/job pair yet."
            }
        return analysis.gap_analysis_data

    if name == "search_knowledge_base":
        query = arguments.get("query", "")
        if not query:
            return {"error": "No search query provided."}
        results = knowledge_service.search(db, query, limit=3)
        return {
            "results": [
                {
                    "topic": chunk.topic,
                    "title": chunk.title,
                    "content": chunk.content,
                    "similarity": round(sim, 4),
                }
                for chunk, sim in results
            ]
        }

    if name == "get_roadmap":
        if resume_id is None or job_id is None:
            return {"error": "Both a resume and a job need to be selected."}
        analysis = analysis_repo.get_latest_for_pair(
            db, user_id, resume_id, job_id
        )
        if analysis is None:
            return {
                "error": "No readiness analysis has been run for this resume/job pair yet."
            }
        roadmap = roadmap_repo.get_by_analysis_id(db, analysis.id)
        if roadmap is None or roadmap.status != RoadmapStatus.ready:
            return {"error": "No roadmap has been generated for this analysis yet."}
        return roadmap.data

    if name == "generate_interview_questions":
        if resume_id is None or job_id is None:
            return {"error": "Both a resume and a job need to be selected."}
        candidate_profile = candidate_profile_repo.get_by_resume_id(
            db, resume_id
        )
        job_profile = job_profile_repo.get_by_job_id(db, job_id)
        if (
            candidate_profile is None
            or candidate_profile.user_id != user_id
            or job_profile is None
            or job_profile.user_id != user_id
        ):
            return {"error": "Both the resume and job need to be parsed first."}

        count = arguments.get("count") or 5
        return interview_service.generate_questions(
            candidate_data=CandidateProfileData(**candidate_profile.data),
            job_data=JobProfileData(**job_profile.data),
            count=count,
        )

    return {"error": f"Unknown tool: {name}"}