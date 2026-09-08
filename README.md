# STRIX — Explainable AI Code Intelligence Platform

**Every Algorithm Has a Story.**

STRIX analyzes your code and explains *how* it reached every conclusion — combining
deterministic static analysis (AST / Tree-sitter) with AI-generated natural-language
explanations. Built for DSA students, interview candidates, and developers who want to
understand *why* their code has the complexity it does, not just be told a number.

🔗 **Live demo:** [your-deployed-url-here]

---

## What it does

- **Analyzes Python, C++, and Java** code for time/space complexity
- **Detects common algorithm patterns**: Bubble Sort, Binary Search, Two Pointer, Two Sum (Brute Force), Duplicate Check (Brute Force)
- **Explains its reasoning** step-by-step via an AI Reasoning Timeline — not just "O(n²)," but *why*
- **Suggests optimizations** when a genuinely better approach is known (e.g. Bubble Sort → built-in sort, brute-force Two Sum → hash map)
- **Visualizes complexity** on an O(1)→O(n!) scale, and **animates** the detected algorithm in action
- **Saves analysis history** per user (Google OAuth), with pin/favorite and rename support
- **Exports a PDF report** of any analysis

## Why it's different

Most AI coding tools guess. STRIX doesn't. Every complexity estimate and algorithm match
carries a **confidence level** (high/medium/low) and a **plain-language rationale** —
and when the static engine genuinely can't tell, it says so honestly instead of fabricating
a confident-sounding answer. The AI layer only *narrates* facts the deterministic engine
already established; it never overrides them.

## Architecture

Backend follows Clean Architecture:
domain/ → pure business entities (no framework dependencies)
application/ → use cases + abstract ports (interfaces)
infrastructure/ → concrete adapters (parsers, detectors, DB, LLM, auth)
api/ → FastAPI routes (composition root)


Frontend follows feature-sliced design (`features/landing`, `features/analysis`, `features/auth`, `features/history`).

## Tech stack

**Backend:** FastAPI · SQLAlchemy · Alembic · Python `ast` + Tree-sitter (C++/Java) · Authlib (Google OAuth) · Ollama (optional local LLM) with automatic template-based fallback

**Frontend:** React · TypeScript · Tailwind CSS · Framer Motion · Monaco Editor · TanStack Query

**Database:** Neon Postgres

**Deployment:** Render (backend) · Vercel (frontend)

## Running locally

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt
cp .env.example .env     # fill in your own values
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Visit `http://localhost:5173`.

## Testing
```bash
cd backend
pytest -v
```
101+ tests covering parsers, detectors, complexity estimation, optimization suggestions, auth, and persistence across all 3 supported languages.

## Project status

Actively developed. Currently supports 5 algorithm patterns across Python/C++/Java, with
more planned. See open items in project notes for algorithm-detection expansion,
best/average/worst-case differentiation, and Benchmark Mode.

---

Built by Namrata Singh.