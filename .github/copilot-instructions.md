# Copilot instructions for this repository

Purpose: help code-generating agents become productive quickly in this project.

- **Big picture**: This repo ingests a PDF, creates embeddings with OpenAI, stores vectors in a Postgres/pgvector collection, and exposes a prompt/search layer used by a simple chat runner.
  - Ingest pipeline: `src/ingest.py` — PyPDFLoader -> `RecursiveCharacterTextSplitter` -> `Document` -> `OpenAIEmbeddings` -> `PGVector`.
  - Search/chat layer: `src/search.py` (prompt template + `search_prompt`) and `src/chat.py` (entrypoint).
  - Infrastructure: `docker-compose.yml` spins up a `pgvector/pgvector` Postgres image used as the vector DB.

- **Key files to inspect and modify**:
  - `src/ingest.py` — canonical ingestion flow and env var validation.
  - `src/search.py` — currently contains `PROMPT_TEMPLATE` and an unimplemented `search_prompt(question=None)`; implement retrieval + prompt assembly here.
  - `src/chat.py` — minimal runner that calls `search_prompt()`.
  - `docker-compose.yml` — starts Postgres with pgvector extension.
  - `requirements.txt` — definitive list of Python packages to install.

- **Required environment variables (must validate in code)**:
  - `OPENAI_API_KEY` — OpenAI credentials used by `OpenAIEmbeddings`.
  - `DATABASE_URL` — connection string for Postgres/pgvector.
  - `PG_VECTOR_COLLECTION_NAME` — collection name used by `PGVector` in `ingest.py`.
  - `PDF_PATH` — path (relative to repo root) to the PDF to ingest.
  - Optional: `OPENAI_MODEL` (defaults to `text-embedding-3-small`).
  - Note: `ingest.py` prints `PGVECTOR_COLLECTION` at the end; prefer using `PG_VECTOR_COLLECTION_NAME` consistently.

- **How to run locally (developer flows)**:
  - Install dependencies: `pip install -r requirements.txt`.
  - Start DB: `docker compose up -d` or `docker-compose up -d` (both are acceptable depending on the environment).
  - Ensure env vars are set (suggest creating a `.env` with keys above).
  - Ingest PDF into the vector DB: `python src/ingest.py`.
  - Run the chat/qa entrypoint: `python src/chat.py` (note: `search_prompt` must be implemented for chat to work).
  - Debug DB: `docker compose logs -f postgres_rag` and `psql` into the container if needed.

- **Project-specific patterns and conventions**:
  - Error-first validation: `ingest.py` validates required env vars at startup and raises `RuntimeError` with Portuguese messages. Follow the same style and messaging when adding checks.
  - Portuguese user-facing messages: keep CLI prints and error messages in Portuguese to preserve UX consistency.
  - Metadata cleaning: `ingest.py` removes empty metadata values before storing Documents; reuse this approach when preparing documents for storage.
  - Deterministic chunk IDs: chunk IDs are created as `doc-{i}` — preserve this or intentionally change with careful migration steps.
  - Vector store usage: `PGVector(..., use_jsonb=True)` is used for storing metadata. When adding retrieval code, instantiate `PGVector` with the same parameters.

- **Implementing `search_prompt` (practical pointers)**:
  - Expected behavior: accept a `question` (or read from caller), perform a similarity search in the same collection used by ingestion, format `PROMPT_TEMPLATE` with retrieved context, and return either a ready-to-run chain or the final answer string.
  - Use the same `OpenAIEmbeddings` model and `PGVector` from `langchain_postgres` as in `ingest.py`.
  - Follow prompt rules in `PROMPT_TEMPLATE`: only answer from context, and respond with the fixed fallback phrase when context lacks the answer.
  - Keep any LLM calls or chains isolated in `src/search.py` to keep `src/chat.py` simple.

- **Integration points & external services**:
  - OpenAI embeddings (via `langchain_openai.OpenAIEmbeddings`).
  - Postgres + pgvector (see `docker-compose.yml` service `postgres` and bootstrap extension step `bootstrap_vector_ext`).
  - Dependencies are declared in `requirements.txt`; prefer using those package names/versions when adding code.

- **Testing & debugging notes**:
  - There are no automated tests in the repo. For verification, run `ingest.py` end-to-end and inspect the Postgres collection for inserted rows.
  - Use the printed logs in `ingest.py` for progress checkpoints (pages loaded, chunks generated, embeddings model used, collection name).

- **PR guidance for AI agents**:
  - Make minimal, focused changes; preserve existing Portuguese messages and env var checks.
  - When adding functionality (e.g., `search_prompt`), include a short local run example in the commit message and update `README.md` with run steps if you add new developer-facing commands.

If anything in this guide is unclear or missing (for example, additional env vars or intended `search_prompt` return type), tell me which section to expand and I will update the file.
