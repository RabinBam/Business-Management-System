# AegisFlow AI

A complete AI-assisted business workflow product built with Next.js, React, FastAPI, SQLite, and Docker.

## Start here

1. Copy `.env.example` to `.env` if you need to change defaults.
2. Run the full stack:

   ```bash
   docker compose up --build
   ```

3. Open the command center at <http://localhost:3000> and API documentation at <http://localhost:8000/docs>.

The default stack uses durable SQLite storage and a deterministic mock AI provider, so every developer can run the complete workflow without credentials. The integrated path covers objective segmentation, task refinement, worker matching and execution, bounded management revisions, cost-aware reports, marketing, watcher events, and the final executive summary. Docker stores application state in the `backend_data` volume, so backend restarts do not erase workflows.

The checked-in configuration does **not** use an OpenAI key. OpenAI calls are enabled only when `AI_PROVIDER=openai`, `AI_PRIMARY_MODEL`, and `OPENAI_API_KEY` are set deliberately. See [the product implementation status](docs/DEV_STATUS.md) for the tested handoffs and deployment boundary.

For shared or production deployments, set a strong `ADMIN_API_KEY`, restrict `TRUSTED_HOSTS` and `FRONTEND_ORIGIN`, provide secrets through the deployment platform, and place the app behind your organization’s identity-aware proxy. Never commit provider keys to Git.

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

The backend acceptance suite also verifies persisted restart recovery, revision re-execution, live dashboard/workforce contracts, cost propagation, and request security controls. The frontend dependency audit is enforced in CI.

