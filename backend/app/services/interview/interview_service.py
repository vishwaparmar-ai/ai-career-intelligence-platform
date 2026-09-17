import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from backend.app.models.candidate_profile import ProfileStatus
from backend.app.models.interview_session import InterviewSession, InterviewSessionStatus
from backend.app.models.job_profile_model import JobProfileStatus
from backend.app.repositories import (
    candidate_profile_repo,
    interview_repo,
    job_profile_repo,
    job_repo,
    resume_repo,
)
from backend.app.schemas.candidate_schema import CandidateProfileData
from backend.app.schemas.job_schema import JobProfileData
from backend.app.services.interview import interview_evaluation_service,interview_question_service

DEFAULT_QUESTION_COUNT = 5
 
 
class InterviewNotPossibleError(Exception):
    pass
 
 
class InterviewSessionNotFoundError(Exception):
    pass
 
 
class InterviewSessionCompleteError(Exception):
    pass
 
 
class InterviewSessionNotCompleteError(Exception):
    pass
 
 
def start_session(
    db: Session,
    *,
    user_id: uuid.UUID,
    resume_id: uuid.UUID,
    job_id: uuid.UUID,
    count: int = DEFAULT_QUESTION_COUNT,
) -> InterviewSession:
    resume = resume_repo.get_resume_for_user(db, resume_id, user_id)
    if resume is None:
        raise InterviewNotPossibleError("Resume not found.")
 
    job = job_repo.get_job_for_user(db, job_id, user_id)
    if job is None:
        raise InterviewNotPossibleError("Job not found.")
 
    candidate_profile = candidate_profile_repo.get_by_resume_id(db, resume_id)
    if candidate_profile is None or candidate_profile.status != ProfileStatus.ready:
        raise InterviewNotPossibleError(
            "Extract this resume's profile first (on the Resume tab)."
        )
 
    job_profile = job_profile_repo.get_by_job_id(db, job_id)
    if job_profile is None or job_profile.status != JobProfileStatus.ready:
        raise InterviewNotPossibleError(
            "Extract this job's requirements first (on the Job tab)."
        )
 
    candidate_data = CandidateProfileData(**candidate_profile.data)
    job_data = JobProfileData(**job_profile.data)
 
    generated = interview_question_service.generate_questions(
        candidate_data=candidate_data, job_data=job_data, count=count
    )
 
    if "error" in generated or not generated.get("questions"):
        raise InterviewNotPossibleError(
            generated.get("error", "Couldn't generate interview questions. Try again.")
        )
 
    questions_state = [
        {
            "question": q["question"],
            "focus_skill": q.get("focus_skill"),
            "answer": None,
            "answered_at": None,
            "evaluation": None,
        }
        for q in generated["questions"]
    ]
 
    session = InterviewSession(
        user_id=user_id,
        resume_id=resume_id,
        job_id=job_id,
        status=InterviewSessionStatus.in_progress,
        questions=questions_state,
        current_index=0,
    )
    return interview_repo.create_session(db, session)
 
 
def get_session(
    db: Session, *, session_id: uuid.UUID, user_id: uuid.UUID
) -> InterviewSession:
    session = interview_repo.get_session_for_user(db, session_id, user_id)
    if session is None:
        raise InterviewSessionNotFoundError("Interview session not found.")
    return session
 
 
def submit_answer(
    db: Session, *, session_id: uuid.UUID, user_id: uuid.UUID, answer: str
) -> InterviewSession:
    session = get_session(db, session_id=session_id, user_id=user_id)
 
    if session.status == InterviewSessionStatus.completed:
        raise InterviewSessionCompleteError("This interview session is already complete.")
 
    idx = session.current_index
    if idx >= len(session.questions):
        raise InterviewSessionCompleteError("This interview session is already complete.")
 
    session.questions[idx]["answer"] = answer
    session.questions[idx]["answered_at"] = datetime.now(timezone.utc).isoformat()
    # JSONB columns don't auto-detect in-place mutation of the underlying
    # dict/list the way a plain column assignment would — flag_modified
    # tells SQLAlchemy explicitly that this attribute needs to be
    # re-persisted, regardless of object identity.
    flag_modified(session, "questions")
 
    session.current_index = idx + 1
    if session.current_index >= len(session.questions):
        session.status = InterviewSessionStatus.completed
 
    return interview_repo.save(db, session)
 
 
def generate_feedback(
    db: Session, *, session_id: uuid.UUID, user_id: uuid.UUID
) -> InterviewSession:
    session = get_session(db, session_id=session_id, user_id=user_id)
 
    if session.status != InterviewSessionStatus.completed:
        raise InterviewSessionNotCompleteError(
            "Answer all the questions before requesting feedback."
        )
 
    job_profile = job_profile_repo.get_by_job_id(db, session.job_id)
    if job_profile is None or job_profile.data is None:
        raise InterviewNotPossibleError("Job details are no longer available.")
    job_data = JobProfileData(**job_profile.data)
 
    qa_pairs = [
        {
            "question": q["question"],
            "focus_skill": q.get("focus_skill"),
            "answer": q.get("answer") or "",
        }
        for q in session.questions
    ]
 
    evaluations = interview_evaluation_service.evaluate_session(
        job_data=job_data, qa_pairs=qa_pairs
    )
 
    for question, evaluation in zip(session.questions, evaluations):
        question["evaluation"] = evaluation
    flag_modified(session, "questions")
 
    return interview_repo.save(db, session)
 