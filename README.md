# AegisFlow AI

A shared two-day MVP foundation for a five-person team building an AI-assisted business workflow system with Next.js, React, FastAPI, and Docker.

## Start here

1. Copy `.env.example` to `.env` if you need to change defaults.
2. Run the full stack:

   ```bash
   docker compose up --build
   ```

3. Open the command center at <http://localhost:3000> and API documentation at <http://localhost:8000/docs>.

The default stack uses in-memory stores and a deterministic mock AI provider, so every developer can run the complete workflow without credentials. The integrated path covers objective segmentation, task refinement, worker execution, management review, reports, marketing, watcher events, and the final executive summary. Restarting the backend clears runtime data; durable storage and the real AI provider remain opt-in extension points.

The checked-in configuration does **not** use an OpenAI key. OpenAI calls are enabled only when `AI_PROVIDER=openai`, `AI_PRIMARY_MODEL`, and `OPENAI_API_KEY` are set deliberately. See [the DEV implementation status](docs/DEV_STATUS.md) for the tested handoffs and current MVP limits.

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
cd backend
ruff check .
pytest
cd ../frontend
npm run check
cd ..
docker compose config --quiet
docker compose build
```

