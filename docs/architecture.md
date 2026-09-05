# Architecture

## 1. System overview

The system is a layered application: a thin Next.js client, a thin FastAPI layer, and a services layer that owns all business logic. Routes never talk to Postgres, Redis, or the LLM directly — everything goes through a service function in `app/services/`. This keeps route handlers thin and makes each dependency mockable in tests.

```
Client (Next.js)
      │
      ▼
FastAPI (API layer)
      │
      ▼
Services (business logic)
      │
      ├──► Postgres + pgvector   (durable data + vector search)
      ├──► Celery + Redis        (background compute)
      └──► API Provider (LLM)      (extraction, generation, embeddings)

Observability (structured logs, latency/error metrics, LLM traces)
      — spans every layer above
```

**Why this shape:** the services layer is the seam that lets each dependency be swapped or mocked independently. If the LLM provider changes, only `services/llm` changes. If pgvector turns out not to scale, only the matching service's data-access calls change — the API contract and the route handlers don't move.

## 2. Request lifecycles

There are two distinct request lifecycles in this system. Conflating them is the most common design mistake at this stage.

### Fast path (synchronous)

Used for anything cheap: login, fetching a saved analysis, listing resumes.

```
Client → FastAPI → service → Postgres → response
```

Single request/response cycle, typically under a few hundred ms.

### Slow path (asynchronous) — resume/job analysis

Used for anything that touches an LLM or does real matching work.

```
1. Client uploads resume + job description
2. FastAPI validates the upload and enqueues a background job, returns a job_id immediately
3. Celery worker: extract resume/job to structured data via LLM
4. Celery worker: normalize skills, embed, match, score
5. Postgres: persist readiness score, gaps, roadmap
6. Client polls job status (or is notified) and fetches the result once ready
```

**Why not synchronous end-to-end:** a full analysis (extraction → normalization → embedding → matching → roadmap generation) can take 10–30+ seconds of LLM latency — well past a reasonable HTTP timeout, and it would tie up a request-handling worker doing nothing but waiting. Returning a `job_id` immediately keeps the API responsive and allows retrying a single failed step without the user re-uploading anything.

**Idempotency:** if a poll request times out and retries, or a worker crashes mid-job and Celery redelivers the task, the system must not double-charge an LLM call or create duplicate analyses. Design the job table with a uniqueness constraint (e.g. on `user_id` + `resume_id` + `job_id`) from the start rather than retrofitting it later.

## 3. Failure paths

| Failure | Handling |
|---|---|
| Corrupted / empty / oversized PDF | Rejected at the FastAPI layer before reaching a worker — cheap, synchronous, clear error to the user |
| LLM call fails or times out | Bounded retry with backoff in the worker; after N attempts, mark the job `failed` with a reason rather than leaving it stuck `processing` |
| LLM returns malformed structured output | Caught by Pydantic validation; retry once with a stricter prompt, then fail loudly rather than persisting invalid data |
| Worker crashes mid-job | Task must be safely re-deliverable (idempotency key); job status reflects reality, never goes stale |
| Database briefly unavailable | Connection pooling + timeouts so one slow query doesn't cascade into request pile-up |
| Malicious / prompt-injected resume content | Resume content is treated as untrusted data — extraction prompts state it is content to extract from, not instructions to follow |
| LLM provider outage | Provider abstraction (`services/llm`) makes a fallback provider possible later; for MVP, fail gracefully with a clear retry message |

## 4. Key trade-offs

- **pgvector vs. a dedicated vector DB (Pinecone, Weaviate):** one fewer moving part and one fewer bill for MVP scale. Revisit only if similarity search becomes a measured bottleneck — unlikely at portfolio-project data volumes.
- **Deterministic + semantic scoring vs. a single LLM-generated score:** a single LLM call is faster to build but unexplainable and non-reproducible (ask it twice, get two different scores). A weighted deterministic formula combined with semantic similarity as one input is slower to build but lets the system state exactly why a candidate scored a given percentage — the core "explainable" pitch of the product.
- **Sync vs. async processing:** async adds complexity (job states, polling, worker infrastructure) in exchange for a responsive API and the ability to retry failed steps independently.
- **LLM provider abstraction:** costs some upfront design to build `services/llm` as an interface rather than calling the SDK directly everywhere, but pays off in testability (mock the interface in unit tests) and flexibility (swap models/providers without touching business logic).

## 5. Non-goals for the MVP

Payments, recruiter marketplace, social features, mobile app, browser extension, custom-trained LLM, Kubernetes.