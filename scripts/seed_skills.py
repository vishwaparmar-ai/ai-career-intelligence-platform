"""
Seeds the skill taxonomy with a starter set of canonical skills and common
aliases. Safe to re-run — existing skills/aliases are left untouched, only
new ones are added.

Run from the project root with:
    python -m scripts.seed_skills
"""

from backend.db.database import SessionLocal
from backend.app.repositories import skill_repo

# canonical name -> alternate spellings/abbreviations seen in the wild.
# Extend this over time as real resumes/jobs surface new variants — this
# is meant to grow, not to be exhaustive on day one.
SEED_DATA: dict[str, list[str]] = {
    "Python": ["python3", "py"],
    "SQL": ["structured query language"],
    "FastAPI": ["fast api", "fastapi"],
    "PostgreSQL": ["postgres", "postgresql", "postgres sql"],
    "MySQL": ["my sql"],
    "SQLAlchemy": ["sql alchemy"],
    "Pydantic": [],
    "Alembic": [],
    "Redis": [],
    "Celery": [],
    "pgvector": ["pg vector"],
    "Docker": [],
    "Kubernetes": ["k8s"],
    "AWS": ["amazon web services"],
    "Git": [],
    "GitHub": ["git hub"],
    "Linux": [],
    "Postman": [],
    "CI/CD": ["ci cd", "continuous integration continuous deployment"],
    "REST APIs": ["rest api", "restful api", "restful apis"],
    "JWT Authentication": ["jwt", "json web token", "json web tokens"],
    "JavaScript": ["js"],
    "TypeScript": ["ts"],
    "Node.js": ["node", "nodejs"],
    "React": ["react.js", "reactjs"],
    "Next.js": ["nextjs"],
    "Pandas": [],
    "NumPy": ["numpy"],
    "Scikit-learn": ["sklearn", "scikit learn"],
    "Machine Learning": ["ml"],
    "Deep Learning": ["dl"],
    "Natural Language Processing": ["nlp"],
    "Large Language Models": ["llms", "llm"],
    "Retrieval-Augmented Generation": ["rag"],
    "LangChain": ["lang chain"],
    "LangGraph": ["lang graph"],
    "ChromaDB": ["chroma db", "chroma"],
}


def run() -> None:
    db = SessionLocal()
    try:
        for canonical_name, aliases in SEED_DATA.items():
            skill = skill_repo.find_skill_by_name_or_alias(db, canonical_name)
            if skill is None:
                skill = skill_repo.create_skill(db, canonical_name)
                print(f"created skill: {canonical_name}")

            for alias in aliases:
                skill_repo.add_alias(db, skill_id=skill.id, alias=alias)

        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    run()