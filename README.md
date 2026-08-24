# AegisFlow AI

A shared two-day MVP foundation for a five-person team building an AI-assisted business workflow system with Next.js, React, FastAPI, and Docker.

## Start here

1. Copy `.env.example` to `.env` if you need to change defaults.
2. Run the full stack:

   ```bash
   docker compose up --build
   ```

3. Open the command center at <http://localhost:3000> and API documentation at <http://localhost:8000/docs>.

The starter uses an in-memory workflow store and a mock AI provider so every developer can work without credentials. Restarting the backend clears created workflows. The database, real AI provider, worker execution, prediction, reports, and marketing generation are intentionally isolated extension points.

## Local development

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Team boundaries

Read [docs/OWNERSHIP.md](docs/OWNERSHIP.md) before coding and [docs/API_CONTRACTS.md](docs/API_CONTRACTS.md) before changing a shared schema. Each person has an owned area, a first task, and a handoff target.

## Quality checks

```bash
cd backend && pytest
cd frontend && npm run check
docker compose config
```

