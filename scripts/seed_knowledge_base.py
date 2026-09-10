"""
Seeds the RAG knowledge base with a small, curated set of chunks across
the topics this project's roadmap specifies: Python, FastAPI, Docker, AWS,
RAG, embeddings, LLMs, PostgreSQL, Git, and system design.

Each entry below is already a coherent, self-contained chunk — written
that way deliberately rather than auto-split from a longer document, so
retrieval quality doesn't depend on where a generic chunker happened to
cut a paragraph in half.

Safe to re-run: it clears existing chunks first and re-inserts, so you can
edit the content below and re-seed without worrying about duplicates.

Run from the project root with:
    python -m scripts.seed_knowledge_base
"""

from backend.db.database import SessionLocal
from backend.app.models.knowledge_chunk_model import KnowledgeChunk
from backend.app.services.rag import knowledge_service

# (topic, title, content)
CHUNKS: list[tuple[str, str, str]] = [
    (
        "Python",
        "Type hints and Pydantic",
        "Python's type hints (e.g. `def f(x: int) -> str`) don't change runtime "
        "behavior on their own — Python still won't stop you from passing a "
        "string where an int is annotated. Their real value comes from tools "
        "built on top of them: editors use them for autocomplete, mypy uses "
        "them for static checking, and Pydantic uses them to actually validate "
        "and coerce data at runtime. That's why FastAPI leans on Pydantic so "
        "heavily — a type hint becomes a real validation rule at the API "
        "boundary, not just documentation.",
    ),
    (
        "Python",
        "Async/await and when it actually helps",
        "`async`/`await` in Python helps when a function spends most of its "
        "time waiting on I/O — a network call, a database query, reading a "
        "file — because the event loop can run other work during that wait "
        "instead of blocking. It does not make CPU-bound code (heavy loops, "
        "number crunching) faster; that still runs on one thread. A common "
        "mistake is marking a route `async def` in FastAPI but calling a "
        "blocking library inside it (like a synchronous DB driver) — that "
        "blocks the whole event loop instead of freeing it up.",
    ),
    (
        "FastAPI",
        "Dependency injection with Depends",
        "FastAPI's `Depends()` lets a route declare what it needs (a DB "
        "session, the current authenticated user, a paginated query "
        "parameter) without constructing it inline. FastAPI calls the "
        "dependency function, and if that function itself has dependencies, "
        "FastAPI resolves those first — dependencies can be nested. This is "
        "what keeps route handlers thin: `get_current_user` and `get_db` are "
        "both just dependency functions, reused across every protected route "
        "instead of duplicated in each one.",
    ),
    (
        "FastAPI",
        "Request validation with Pydantic models",
        "When a FastAPI route takes a Pydantic model as a parameter, incoming "
        "JSON is validated against that model automatically before your "
        "function body runs — invalid data never reaches your code, and "
        "FastAPI returns a 422 with the exact validation errors on its own. "
        "This is why routes can assume `payload.email` is a valid email "
        "string by the time they touch it: the validation already happened "
        "at the boundary, not scattered through business logic.",
    ),
    (
        "Docker",
        "Images vs. containers",
        "A Docker image is a static, layered snapshot — the filesystem plus "
        "metadata about how to run it — built once from a Dockerfile. A "
        "container is a running (or stopped) instance of that image, with "
        "its own writable layer on top. You can start many containers from "
        "the same image; each gets an isolated filesystem and process space "
        "but shares the underlying image layers on disk, which is why "
        "spinning up a new container from an existing image is fast.",
    ),
    (
        "Docker",
        "Multi-stage builds",
        "A multi-stage Dockerfile uses more than one `FROM` line — typically "
        "one stage with the full build toolchain (compilers, dev "
        "dependencies) that produces build artifacts, and a second, minimal "
        "stage that copies only those artifacts in. This keeps the final "
        "image small and free of build-time tooling that has no reason to "
        "exist in production, which matters for both image pull speed and "
        "reducing the attack surface of what ships.",
    ),
    (
        "AWS",
        "EC2 vs. ECS vs. Lambda for a backend API",
        "EC2 gives you a raw virtual machine — full control, but you manage "
        "the OS, scaling, and deployment yourself. ECS (or EKS) runs "
        "containers for you on a managed cluster, handling restarts and "
        "scaling policies, at the cost of more setup than EC2 alone. Lambda "
        "runs your code per-request with no server to manage at all, but "
        "cold starts and execution time limits make it a poor fit for a "
        "long-running FastAPI app with a persistent DB connection pool — "
        "ECS/Fargate is the more natural fit for that shape of app.",
    ),
    (
        "AWS",
        "RDS and managed Postgres",
        "RDS runs PostgreSQL (or other engines) as a managed service — AWS "
        "handles patching, automated backups, and failover, in exchange for "
        "less low-level control than self-hosting Postgres on an EC2 "
        "instance. For a small project, RDS's main cost trade-off is that "
        "you're paying for the managed layer even at low traffic; the "
        "operational trade-off is that you don't have to be the one paging "
        "yourself at 2am for a disk-full error.",
    ),
    (
        "RAG",
        "What RAG is and why it reduces hallucination",
        "Retrieval-Augmented Generation means: before asking an LLM to "
        "answer, first retrieve relevant text from a known, trusted source, "
        "then include that text in the prompt as context. The model is "
        "answering from what it was just given, not purely from what it "
        "memorized during training — which is why RAG reduces (not "
        "eliminates) hallucination and lets an application answer "
        "accurately about content the model was never trained on, like a "
        "specific company's internal docs.",
    ),
    (
        "RAG",
        "The retrieval pipeline stages",
        "A RAG pipeline has five stages: chunk (split source documents into "
        "manageable pieces), embed (turn each chunk into a vector), store "
        "(save vectors plus the original text and metadata), retrieve (embed "
        "the incoming query, find the closest stored vectors), and augment "
        "+ generate (insert the retrieved text into the prompt and let the "
        "LLM answer from it). Quality problems usually trace back to "
        "chunking (chunks too big or badly split) or retrieval (wrong top-k, "
        "no relevance filtering) more often than the generation step itself.",
    ),
    (
        "Embeddings",
        "What an embedding actually is",
        "An embedding is a list of numbers (a vector) that represents the "
        "meaning of a piece of text, produced by a model trained so that "
        "texts with similar meaning end up with similar vectors — even if "
        "they don't share any of the same words. That's the key property "
        "that keyword search doesn't have: 'built scalable backend systems' "
        "and 'designed APIs that handled high request volume' can land close "
        "together in embedding space despite zero word overlap.",
    ),
    (
        "Embeddings",
        "Cosine similarity",
        "Cosine similarity measures the angle between two vectors, not their "
        "distance or magnitude — two embeddings pointing in nearly the same "
        "direction score close to 1 (very similar) regardless of how long "
        "each vector is. This matters for embeddings specifically because "
        "vector magnitude often reflects things like text length rather than "
        "meaning, so comparing direction (cosine) gives a more meaning-"
        "focused similarity than comparing raw distance would.",
    ),
    (
        "LLMs",
        "Tool use / function calling",
        "Tool use lets you give a model a set of function definitions (name, "
        "description, and a JSON schema for its arguments) and have the "
        "model respond by choosing to 'call' one, with arguments matching "
        "that schema, instead of just writing prose. This is the mechanism "
        "structured extraction relies on: instead of asking a model to "
        "'return JSON' in a text response and hoping it's well-formed, "
        "forcing a tool call makes the output's shape enforced by the API "
        "itself, not just requested in the prompt.",
    ),
    (
        "LLMs",
        "Context windows and why chunking matters",
        "A model's context window is the maximum number of tokens (roughly, "
        "word-pieces) it can consider at once, across the system prompt, "
        "conversation history, and any retrieved content. Anything beyond "
        "that limit simply isn't seen by the model at generation time. This "
        "is a second, independent reason RAG chunks documents rather than "
        "dumping them in whole — even a moderately sized document can "
        "exceed a usable context budget once combined with instructions and "
        "conversation history.",
    ),
    (
        "PostgreSQL",
        "Indexes and query performance",
        "Without an index, Postgres checks every row to satisfy a filter — a "
        "sequential scan. An index on a frequently-filtered column (like "
        "`users.email` in a login lookup) lets Postgres jump straight to "
        "matching rows instead. Indexes aren't free, though: every insert or "
        "update also has to update every index on that table, so indexing "
        "every column 'just in case' trades write performance for read "
        "performance you may not need.",
    ),
    (
        "PostgreSQL",
        "JSONB columns",
        "JSONB stores JSON in a decomposed binary format rather than as "
        "plain text (the older `json` type), which makes it faster to query "
        "and index at the cost of slightly slower writes. It's a reasonable "
        "fit for data that's naturally document-shaped and doesn't need "
        "relational integrity — an LLM's structured extraction output, for "
        "instance — without going through the ceremony of encoding every "
        "possible nested field as its own column and migration.",
    ),
    (
        "Git",
        "Branching strategy basics",
        "A simple, effective default for a solo or small-team project is: "
        "`main` always stays deployable, and every feature or fix gets its "
        "own short-lived branch merged back via a pull request once it "
        "works. The point isn't the specific branch names — it's keeping "
        "`main` in a state you could deploy at any moment, so a broken "
        "half-finished change never blocks anyone (including future-you) "
        "from shipping something else.",
    ),
    (
        "Git",
        "Rebase vs. merge",
        "`git merge` creates a new commit that ties two branch histories "
        "together, preserving exactly what happened, including the branch "
        "structure. `git rebase` replays your branch's commits on top of "
        "another branch's latest state, producing a linear history with no "
        "merge commit — cleaner to read, but it rewrites commit hashes, "
        "which is why rebasing a branch other people have already pulled is "
        "generally avoided: their history and yours will no longer match.",
    ),
    (
        "System design",
        "Horizontal vs. vertical scaling",
        "Vertical scaling means giving a single server more resources (more "
        "CPU, more RAM) — simple, but it has a hard ceiling and that one "
        "server stays a single point of failure. Horizontal scaling means "
        "running more instances of your app behind a load balancer instead "
        "— it scales further and survives one instance failing, but it "
        "requires the app itself to be stateless (or externalize state to a "
        "shared store like a database or Redis), since you can no longer "
        "assume two requests land on the same machine.",
    ),
    (
        "System design",
        "Caching basics",
        "Caching stores the result of expensive work (a slow query, an "
        "external API call, a computed score) so a repeat request can skip "
        "redoing it. The two questions that matter most are what to cache "
        "(data that's read often relative to how often it changes) and how "
        "to invalidate it (deleting or updating the cached value when the "
        "underlying data changes) — a cache with no invalidation strategy "
        "just serves stale data forever once something changes upstream.",
    ),
]


def run() -> None:
    db = SessionLocal()
    try:
        existing = db.query(KnowledgeChunk).count()
        if existing:
            db.query(KnowledgeChunk).delete()
            db.commit()
            print(f"Cleared {existing} existing chunk(s).")

        # chunk_index counts each topic's chunks separately, starting at 0
        topic_counters: dict[str, int] = {}

        for topic, title, content in CHUNKS:
            index = topic_counters.get(topic, 0)
            knowledge_service.ingest_chunk(
                db, topic=topic, title=title, content=content, chunk_index=index
            )
            topic_counters[topic] = index + 1
            print(f"embedded: [{topic}] {title}")

        print(f"Seed complete — {len(CHUNKS)} chunks across {len(topic_counters)} topics.")
    finally:
        db.close()


if __name__ == "__main__":
    run()