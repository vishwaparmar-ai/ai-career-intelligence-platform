import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.skills_model import Skill
from backend.app.models.skill_alias_model import SkillAlias


def normalize_text(value: str) -> str:
    """Lowercase and collapse whitespace — the same normalization used for
    every lookup, so 'Fast   API' and 'fast api' hit the same alias row."""
    return " ".join(value.strip().lower().split())


def find_skill_by_name_or_alias(db: Session, raw_skill: str) -> Skill | None:
    normalized = normalize_text(raw_skill)

    # A canonical name is implicitly its own alias — check it first so a
    # perfectly-formed "FastAPI" doesn't need an explicit alias row at all.
    skill = db.query(Skill).filter(func.lower(Skill.name) == normalized).first()
    if skill:
        return skill

    alias = (
        db.query(SkillAlias)
        .filter(SkillAlias.normalized_alias == normalized)
        .first()
    )
    return alias.skill if alias else None


def create_skill(db: Session, name: str) -> Skill:
    skill = Skill(name=name)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


def add_alias(db: Session, *, skill_id: uuid.UUID, alias: str) -> SkillAlias:
    normalized = normalize_text(alias)

    existing = (
        db.query(SkillAlias)
        .filter(SkillAlias.normalized_alias == normalized)
        .first()
    )
    if existing:
        return existing

    row = SkillAlias(skill_id=skill_id, normalized_alias=normalized)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_skills(db: Session) -> list[Skill]:
    return db.query(Skill).order_by(Skill.name).all()