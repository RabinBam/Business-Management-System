# Byapari

A complete AI-assisted business workflow product built with Next.js, React, FastAPI, SQLite, and Docker.

## Start here

For a step-by-step PC installation with your own OpenRouter key, read
[the Windows installation and presentation guide](docs/INSTALL_WINDOWS.md).
Windows users can double-click `Start-Byapari.cmd` after starting Docker Desktop.

1. Copy `.env.example` to `.env` if you need to change defaults.
2. Run the full stack:

   ```bash
   docker compose -f docker-compose.yml up -d --build --wait
   ```

3. Open the command center at <http://localhost:3000> and API documentation at <http://localhost:8000/docs>.

The default stack uses durable SQLite storage and a deterministic mock AI provider, so every developer can run the complete workflow without credentials. The integrated path covers objective segmentation, task refinement, worker matching and execution, bounded management revisions, cost-aware reports, marketing, watcher events, and the final executive summary. Docker stores application state in the `backend_data` volume. Presentation mode backs up and resets saved work on backend startup; set `RESET_DEMO_ON_START=false` to retain it.

Put your own key in the root `.env` file (ignored by Git). OpenRouter is enabled
with `AI_PROVIDER=openrouter`, `AI_PRIMARY_MODEL=provider/model-id`, and
`OPENROUTER_API_KEY=your-key`. Choose a model supporting structured outputs.
Leave `AI_WORKER_MODEL` blank to reuse the primary model. OpenAI remains available
with `AI_PROVIDER=openai`, `AI_PRIMARY_MODEL`, and `OPENAI_API_KEY`.
Keys are passed only to the backend. Rerun the Compose command after editing `.env`.
Never put a secret in a `NEXT_PUBLIC_` variable.

Real AI generates plans, written worker deliverables, reviews, marketing, and
executive summaries. Worker matching, financial calculations, and forecasts from
your supplied monthly revenue history remain deterministic. Business task costs are estimates,
not measured API usage. The app does not perform external business actions.

For shared or production deployments, set a strong `ADMIN_API_KEY`, restrict `TRUSTED_HOSTS` and `FRONTEND_ORIGIN`, provide secrets through the deployment platform, and place the app behind your organization’s identity-aware proxy. Never commit provider keys to Git.

## Local development

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --env-file ../.env
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

## Team boundaries

Read [docs/OWNERSHIP.md](docs/OWNERSHIP.md) before coding and [docs/API_CONTRACTS.md](docs/API_CONTRACTS.md) before changing a shared schema. Each person has an owned area, a first task, and a handoff target.

## Quality checks

```bash
cd backend
ruff check .
# Isolate acceptance tests from your saved workflows and configured provider:
# PowerShell: $env:DATABASE_URL="sqlite:///:memory:"; $env:AI_PROVIDER="mock"
pytest
cd ../frontend
npm run check
cd ..
docker compose config --quiet
docker compose build
```

The backend acceptance suite also verifies persisted restart recovery, revision re-execution, live dashboard/workforce contracts, cost propagation, and request security controls. The frontend dependency audit is enforced in CI.


## Working with employees

Choose employee submission when creating an objective. AI plans distinct work for
all six retained employees, explains each task for their experience, and includes
department handoff notes. Employees select their name, read the task, paste their
work, and submit it. Management reviews submitted work before reports, marketing,
and the CEO summary are generated. Tasks & teams tracks submission and completion.

Money records actual income and expenses separately from the workflow planning
budget. Task estimates receive 60% of that budget; marketing is capped at the
remaining amount. No salary, transfer, ad purchase, or API payment is made.
Fresh installations start without workflows or financial records. The employee
selector is intended for a local demonstration; it is not employee authentication.

Demo controls: AI Workforce - Quick complete tasks (demo), and Command Center -
Reset demo data. Completion is simulated and labeled. Reset preserves employees
and API configuration and backs up the database. Browser refresh does not reset.
