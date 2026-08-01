# STRIX — Explainable AI Code Intelligence Platform

**Every Algorithm Has a Story.**

STRIX combines deterministic static analysis (Python AST / Tree-sitter) with LLM reasoning to
explain *how* it reaches every conclusion about your code — complexity, algorithm identity,
and optimization suggestions — rather than just asserting an answer.

## Status
🚧 Milestone 1: Project scaffolding (this commit).

## Running locally

### Option A — Docker Compose (recommended)
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```
- Backend: http://localhost:8000 (docs at `/docs`)
- Frontend: http://localhost:5173

### Option B — Run natively

**Backend:**
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env    # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Testing
```bash
# Backend (after installing requirements-dev.txt)
cd backend && pytest

# Frontend
cd frontend && npm run build
```

## Architecture
See `PROJECT_PRD.md` for full product vision. Backend follows Clean Architecture
(`domain` → `application` → `infrastructure` / `api`). Frontend follows feature-sliced
design (`features/*` own their own components, hooks, and API calls).
