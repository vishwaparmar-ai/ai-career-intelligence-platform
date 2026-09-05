# AI Career Intelligence Platform

> Upload a resume and a job description. Get an evidence-backed readiness score, an explainable skill-gap analysis, a personalized 30-day roadmap, and AI-driven interview practice — all grounded in your actual profile and the actual job, not a generic LLM guess.

**Status:** 🚧 In active development
**Live demo:** _coming soon_

---

## Why this project exists

Most "AI resume tools" output an opaque score from a single LLM call. This project is built to demonstrate production AI engineering, not just a prompt wrapper:

- Deterministic, explainable scoring combined with semantic (embedding-based) matching
- Structured LLM outputs validated end-to-end with Pydantic
- A small, controlled RAG layer instead of an ungrounded chatbot
- Real backend engineering: auth, migrations, background jobs, rate limiting, observability
- An actual evaluation methodology with a golden dataset — not invented metrics

## Core user journey

```
Resume (PDF) ──┐
                ├─► Structured extraction ─► Skill normalization ─┐
Job description ┘                                                  ├─► Matching (rules + semantic)
                                                                    ├─► Readiness score (explainable)
                                                                    ├─► Skill-gap analysis
                                                                    ├─► Personalized 30-day roadmap
                                                                    └─► Job-specific interview simulator
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js + TypeScript, Tailwind + shadcn/ui |
| Backend | Python + FastAPI, Pydantic |
| Database | PostgreSQL + pgvector, SQLAlchemy, Alembic |
| Background jobs | Redis + Celery |
| AI | LLM API (structured extraction, RAG, interview generation), embeddings |
| Testing | pytest, frontend test suite |
| Deployment | Docker, AWS |
| CI/CD | GitHub Actions |
| Observability | Structured logs, OpenTelemetry / Langfuse |

## Repository structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/            # Route handlers only — no business logic here
│   │   ├── core/           # Config, security, shared setup
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic request/response + LLM output schemas
│   │   ├── services/
│   │   │   ├── resume/     # Resume parsing & structured extraction
│   │   │   ├── job/        # Job description parsing & structured extraction
│   │   │   ├── matching/   # Deterministic + semantic scoring engine
│   │   │   ├── rag/        # Retrieval layer for the knowledge base
│   │   │   ├── interview/  # Interview question generation & answer evaluation
│   │   │   └── llm/        # Provider abstraction for all LLM calls
│   │   ├── repositories/   # Data access layer
│   │   ├── workers/        # Celery background tasks
│   │   └── main.py         # FastAPI app entrypoint
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── api/
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Next.js app (scaffolded separately)
├── docs/                    # Architecture notes, evaluation write-up, product spec
├── scripts/                 # One-off utility / migration / seed scripts
└── README.md
```

## Local setup (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DATABASE_URL, LLM_API_KEY, etc.
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`

## Roadmap

This project follows a 27-day daily roadmap from product spec through deployed, observable MVP. See [`docs/`](./docs) for the product requirements doc, architecture diagram, and evaluation methodology as they're written.

**Non-goals for the MVP:** payments, recruiter marketplace, social features, mobile app, browser extension, custom-trained LLM, Kubernetes.

## What I'd improve at scale

_To be written at the end of the build — see `docs/` for the final write-up._
