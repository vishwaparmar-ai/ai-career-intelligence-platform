from sqlalchemy.orm import Session

from backend.app.repositories import skill_repo


def normalize_skill(db: Session, raw_skill: str) -> str:
    """
    Returns the canonical form of a raw skill string, e.g. 'Fast API' or
    'postgres' -> 'FastAPI' / 'PostgreSQL'. If the taxonomy doesn't
    recognize it, the trimmed original is returned unchanged rather than
    dropped — an unrecognized skill is still a real skill, just not yet
    mapped to a canonical form. This keeps normalization safe to run on
    every resume/job even before the taxonomy covers everything.
    """
    raw_skill = raw_skill.strip()
    if not raw_skill:
        return raw_skill

    skill = skill_repo.find_skill_by_name_or_alias(db, raw_skill)
    return skill.name if skill else raw_skill


def normalize_skills(db: Session, raw_skills: list[str]) -> list[str]:
    """
    Normalizes a whole list and collapses duplicates that resolve to the
    same canonical skill (e.g. ['FastAPI', 'Fast API'] -> ['FastAPI']),
    preserving first-seen order.
    """
    seen: set[str] = set()
    result: list[str] = []

    for raw in raw_skills:
        canonical = normalize_skill(db, raw)
        key = canonical.lower()
        if key not in seen:
            seen.add(key)
            result.append(canonical)

    return result