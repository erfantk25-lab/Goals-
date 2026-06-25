# Architecture Decision Record (ADR) & Trade-offs

## 1. Using SQLite for Testing
**Decision:** We overridden the PostgreSQL database URI in `tests/conftest.py` to use an in-memory `sqlite:///:memory:` database during Pytest execution.
**Trade-off:** 
- *Pros:* Tests run in milliseconds and require zero external dependencies (no Docker required for CI).
- *Cons:* SQLite does not natively support PostgreSQL's `JSONB` datatype.
- *Resolution:* Implemented SQLAlchemy's `.with_variant()` feature to dynamically fall back to standard `JSON` when the test dialect is SQLite, retaining both speed and compatibility.

## 2. Decoupled Service Layer
**Decision:** Abstracted all business logic from FastAPI controllers into `GoalService`.
**Trade-off:**
- *Pros:* Greatly improves testability and keeps routers incredibly clean. Allows the ML pipeline to be reused in offline batch scripts without needing HTTP requests.
- *Cons:* Adds slight boilerplate and an extra layer of indirection.

## 3. Mocking LLM API Responses
**Decision:** Implemented a fallback mock JSON responder in `LLMService` if `OPENAI_API_KEY` is not present.
**Trade-off:**
- *Pros:* Prevents the application from crashing in unconfigured CI/CD runners or local portfolio demonstrations.
- *Cons:* Can hide genuine network errors if not logged correctly (we added `logger.warning` to mitigate this).

## 4. Prompt Versioning as Files
**Decision:** Prompts are stored in `prompts/v1.txt` rather than hardcoded in Python strings.
**Trade-off:**
- *Pros:* Allows non-engineers (Prompt Engineers / Data Scientists) to tweak LLM behaviors without modifying the application code. Enables Git-based tracking of prompt changes over time.
- *Cons:* Requires disk I/O to load the prompt (mitigated by fast SSDs and potential future caching).
