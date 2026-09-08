from sqlalchemy.orm import Session

from backend.app.schemas.candidate_schema import CandidateProfileData
from backend.app.schemas.gap_analysis_schema import GapAnalysis, SkillGap
from backend.app.schemas.job_schema import JobProfileData
from backend.app.services.matching import skill_taxonomy


_IMPORTANCE_WEIGHT = {"required": 2, "preferred": 1}
_EVIDENCE_WEIGHT = {"missing": 2, "partial": 1, "matched": 0}


def _find_partial_evidence(
    db: Session, skill: str, candidate_data: CandidateProfileData
) -> str | None:
    """
    Looks for the skill anywhere OTHER than the candidate's formal skills
    list — a project's tech stack, or mentioned in passing in an
    experience/project description. This is deliberately weaker evidence
    than a direct skill-list match, which is exactly why it's "partial"
    and not "matched".
    """
    skill_lower = skill.lower()

    for proj in candidate_data.projects:
        project_techs_lower = {
            skill_taxonomy.normalize_skill(db, t).lower()
            for t in proj.technologies
        }
        if skill_lower in project_techs_lower:
            return f"Used in project: {proj.name}"
        if any(skill_lower in line.lower() for line in proj.description):
            return f"Mentioned in project: {proj.name}"

    for exp in candidate_data.experience:
        if any(skill_lower in line.lower() for line in exp.description):
            label = exp.title or "a previous role"
            return f"Mentioned in experience: {label}"

    return None


def _classify_skill(
    db: Session,
    skill: str,
    importance: str,
    candidate_skills_lower: set[str],
    candidate_data: CandidateProfileData,
) -> SkillGap:
    skill_lower = skill.lower()

    if skill_lower in candidate_skills_lower:
        status = "matched"
        evidence = "Listed directly in the candidate's skills"
    else:
        evidence = _find_partial_evidence(db, skill, candidate_data)
        status = "partial" if evidence else "missing"

    priority = _IMPORTANCE_WEIGHT[importance] * _EVIDENCE_WEIGHT[status]

    return SkillGap(
        skill=skill,
        importance=importance,
        status=status,
        evidence=evidence,
        priority=priority,
    )


def compute_gap_analysis(
    db: Session, candidate_data: CandidateProfileData, job_data: JobProfileData
) -> GapAnalysis:
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

    gaps = [
        _classify_skill(db, skill, "required", candidate_skills_lower, candidate_data)
        for skill in required_normalized
    ] + [
        _classify_skill(db, skill, "preferred", candidate_skills_lower, candidate_data)
        for skill in preferred_normalized
    ]

    gaps.sort(key=lambda g: g.priority, reverse=True)

    return GapAnalysis(gaps=gaps)