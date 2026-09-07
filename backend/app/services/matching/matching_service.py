import re
from datetime import date

from sqlalchemy.orm import Session

from backend.app.schemas.analysis_schema import (
    EducationMatchDetail,
    ExperienceMatchDetail,
    MatchResult,
    ProjectMatchDetail,
    SkillMatchDetail,
)
from backend.app.schemas.candidate_schema import CandidateProfileData, EducationEntry, ExperienceEntry
from backend.app.schemas.job_schema import JobProfileData
from backend.app.services.matching import skill_taxonomy

# Configurable, per the roadmap's Day 16 spec. semantic is a real weight
# slot, not a rounding fudge — it scores 0.0 until Day 17 wires in actual
# embedding similarity, at which point only that one function changes.
WEIGHTS: dict[str, float] = {
    "required_skills": 0.40,
    "experience": 0.20,
    "projects": 0.15,
    "preferred_skills": 0.10,
    "semantic": 0.10,
    "education": 0.05,
}


# ---- skills -----------------------------------------------------------


def _score_skill_overlap(
    candidate_skills_lower: set[str], target_skills: list[str]
) -> SkillMatchDetail:
    if not target_skills:
        # Nothing to require/prefer means nothing to be missing — a job
        # with no preferred skills listed shouldn't drag the score down.
        return SkillMatchDetail(matched=[], missing=[], score=1.0)

    matched = [s for s in target_skills if s.lower() in candidate_skills_lower]
    missing = [s for s in target_skills if s.lower() not in candidate_skills_lower]
    return SkillMatchDetail(
        matched=matched, missing=missing, score=len(matched) / len(target_skills)
    )


# ---- experience ---------------------------------------------------------

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _parse_resume_date(value: str | None, *, is_end: bool) -> date | None:
    """
    Best-effort parser for the free-text date formats resumes actually use
    ('09/2025', '2022', 'Jan 2022', 'Present'). Returns None for anything
    it can't confidently parse, rather than guessing — an unparsed date
    just doesn't contribute to the years total instead of corrupting it.
    """
    if not value:
        return None
    text = value.strip().lower()

    if text in ("present", "current", "now", "ongoing"):
        return date.today()

    if m := re.match(r"^(\d{1,2})[/-](\d{4})$", text):
        month, year = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return date(year, month, 1)

    if m := re.match(r"^([a-z]+)\s+(\d{4})$", text):
        month = _MONTHS.get(m.group(1)[:3])
        if month:
            return date(int(m.group(2)), month, 1)

    if m := re.match(r"^(\d{4})$", text):
        year = int(m.group(1))
        return date(year, 12 if is_end else 1, 1)

    return None


def _total_experience_years(experience: list[ExperienceEntry]) -> float:
    total_days = 0
    for exp in experience:
        start = _parse_resume_date(exp.start_date, is_end=False)
        end = _parse_resume_date(exp.end_date, is_end=True)
        if start and end and end > start:
            total_days += (end - start).days
    # Deliberately not de-duplicating overlapping roles — acceptable
    # simplification for an MVP; worth flagging as a known limitation in
    # the Day 28 evaluation writeup.
    return round(total_days / 365.25, 1)


def _score_experience(
    candidate_years: float, min_years: int | None
) -> ExperienceMatchDetail:
    if not min_years or min_years <= 0:
        return ExperienceMatchDetail(
            candidate_years=candidate_years, required_years=None, score=1.0
        )
    score = min(candidate_years / min_years, 1.0)
    return ExperienceMatchDetail(
        candidate_years=candidate_years, required_years=float(min_years), score=score
    )


# ---- projects -----------------------------------------------------------


def _score_projects(
    db: Session, projects, required_skills_normalized: list[str]
) -> ProjectMatchDetail:
    if not required_skills_normalized:
        return ProjectMatchDetail(matched_skills=[], score=1.0 if projects else 0.5)

    project_skills_lower = {
        skill_taxonomy.normalize_skill(db, tech).lower()
        for p in projects
        for tech in p.technologies
    }
    matched = [
        s for s in required_skills_normalized if s.lower() in project_skills_lower
    ]
    return ProjectMatchDetail(
        matched_skills=matched, score=len(matched) / len(required_skills_normalized)
    )


# ---- education ------------------------------------------------------------

_DEGREE_LEVELS: list[tuple[int, str, list[str]]] = [
    (3, "PhD", ["phd", "doctorate", "doctoral"]),
    (2, "Master's", ["master", "m.tech", "m.sc", "mba", "postgraduate", "post-graduate"]),
    (1, "Bachelor's", ["bachelor", "b.tech", "b.sc", "b.e.", "undergraduate"]),
]


def _degree_level(text: str) -> tuple[int, str | None]:
    lowered = text.lower()
    for level, label, keywords in _DEGREE_LEVELS:
        if any(k in lowered for k in keywords):
            return level, label
    return 0, None


def _score_education(
    candidate_education: list[EducationEntry], requirements: list[str]
) -> EducationMatchDetail:
    candidate_level, candidate_label = max(
        (_degree_level(e.degree or "") for e in candidate_education),
        default=(0, None),
        key=lambda x: x[0],
    )

    if not requirements:
        return EducationMatchDetail(
            candidate_level=candidate_label, required_level=None, score=1.0
        )

    required_level, required_label = max(
        (_degree_level(r) for r in requirements), default=(0, None), key=lambda x: x[0]
    )

    if required_level == 0:
        # The posting mentions education but not in a way we recognize as
        # a degree level (e.g. "relevant field") — don't penalize for it.
        return EducationMatchDetail(
            candidate_level=candidate_label, required_level=None, score=1.0
        )

    score = 1.0 if candidate_level >= required_level else 0.0
    return EducationMatchDetail(
        candidate_level=candidate_label, required_level=required_label, score=score
    )


# ---- entrypoint -----------------------------------------------------------


def compute_match(
    db: Session, candidate_data: CandidateProfileData, job_data: JobProfileData
) -> MatchResult:
    candidate_skills_normalized = skill_taxonomy.normalize_skills(
        db, candidate_data.skills
    )
    candidate_skills_lower = {s.lower() for s in candidate_skills_normalized}

    required_normalized = skill_taxonomy.normalize_skills(
        db, job_data.required_skills or []
    )
    preferred_normalized = skill_taxonomy.normalize_skills(
        db, job_data.preferred_skills or []
    )

    required_detail = _score_skill_overlap(candidate_skills_lower, required_normalized)
    preferred_detail = _score_skill_overlap(candidate_skills_lower, preferred_normalized)

    candidate_years = _total_experience_years(candidate_data.experience)
    experience_detail = _score_experience(candidate_years, job_data.min_years_experience)

    projects_detail = _score_projects(db, candidate_data.projects, required_normalized)

    education_detail = _score_education(
        candidate_data.education, job_data.education_requirements or []
    )

    # TODO (Day 17): replace with cosine similarity between candidate and
    # job embeddings via pgvector. Kept as an explicit 0.0 rather than
    # dropped, so today's scores are comparable to tomorrow's once this
    # component goes live — only this line changes.
    semantic_score = 0.0

    overall = (
        WEIGHTS["required_skills"] * required_detail.score
        + WEIGHTS["experience"] * experience_detail.score
        + WEIGHTS["projects"] * projects_detail.score
        + WEIGHTS["preferred_skills"] * preferred_detail.score
        + WEIGHTS["semantic"] * semantic_score
        + WEIGHTS["education"] * education_detail.score
    )

    return MatchResult(
        overall_score=round(overall * 100, 1),
        required_skills=required_detail,
        preferred_skills=preferred_detail,
        experience=experience_detail,
        projects=projects_detail,
        education=education_detail,
        semantic_score=semantic_score,
        weights=WEIGHTS,
    )