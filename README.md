# GET_SET_MARKS — AI-Powered Exam Prep Platform

> RAG-based backend for Tamil Nadu board students (Classes 9–12) — powered by FastAPI, pgvector, and multi-LLM routing.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI (Python) |
| Database | PostgreSQL + pgvector (Supabase) |
| Vector Search | pgvector (RAG retrieval) |
| Cache | Redis (24h RAG cache + rate limiting) |
| Storage | MinIO (S3-compatible PDF storage) |
| Background Jobs | arq (Redis-backed workers) |
| LLM — RAG Chat | DeepSeek V4 / Gemini 2.5 Flash-Lite |
| LLM — Eval | Claude Haiku 4.5 / Gemini 2.5 Flash |
| LLM — Tamil | Gemini 2.5 Flash |
| Auth | Google OAuth 2.0 + JWT |

---

## Project Structure

```
backend/
+-- .env              # Local secrets (NEVER commit — gitignored)
+-- .env.example      # Safe template for teammates
+-- .gitignore        # Excludes secrets, caches, venvs
+-- README.md         # This file
```

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/kaviyashivam1996-lab/GET_SET_MARKS.git
cd GET_SET_MARKS
```

### 2. Set up environment
```bash
cp .env.example .env
# Fill in your secrets in .env
```

### 3. Install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 4. Run the backend
```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000

---

## Environment Variables

Copy .env.example to .env and fill in:

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL async connection string (Supabase) |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_ANON_KEY | Supabase publishable key |
| SUPABASE_SERVICE_ROLE_KEY | Supabase admin key (server-side only) |
| REDIS_URL | Redis connection URL |
| DEEPSEEK_API_KEY | DeepSeek API key |
| GEMINI_API_KEY | Google Gemini API key |
| ANTHROPIC_API_KEY | Anthropic Claude API key |
| JWT_SECRET | Strong random secret for JWT signing |

> ?? Never commit .env — it is gitignored.

---

## Author

**Kaviya Paramasivam** — [@kaviyashivam1996-lab](https://github.com/kaviyashivam1996-lab)
