# DEV implementation status

This file records the repository's implementation status against the supplied
`DEV.md` build and handoff checklist. It describes the current in-memory MVP,
not a production deployment.

## End-to-end path

The default `AI_PROVIDER=mock` path is implemented and does not require or use
an OpenAI API key:

1. `POST /api/v1/workflows` validates and creates a workflow.
2. `POST /api/v1/workflows/{id}/run` executes the guarded state machine.
3. The orchestrator segments the objective and management refines the tasks.
4. Worker matching and execution return validated results for every task.
5. Management reviews the results before report generation.
6. The report service produces auditable financial and prediction data.
7. Marketing generation uses approved report context and enforces the budget
   again in Python before persistence.
8. Management creates the executive summary and completes the workflow.
9. Watcher status and events expose retries, failures, recoveries, and resolved
   workflow stage changes.

## DEV handoff contracts

| Requirement | Status | Public contract |
| --- | --- | --- |
| Create and read workflows | Complete | `POST /workflows`, `GET /workflows/{id}` |
| Read generated tasks | Complete | `GET /workflows/{id}/tasks` |
| Run the managed workflow | Complete | `POST /workflows/{id}/run` |
| Read and regenerate reports | Complete | `GET /workflows/{id}/reports`, `POST /workflows/{id}/reports/generate` |
| Read, generate, and validate marketing plans | Complete | `GET`, `POST`, and `PUT /workflows/{id}/marketing...` |
| Read watcher state and events | Complete | `GET /watcher`, `/watcher/status`, `/watcher/events` |
| Read the final executive summary | Complete | Included in the completed workflow response |
| Interactive API documentation | Complete | `/docs` and `/openapi.json` |
| Credential-free local execution | Complete | Mock provider is the checked-in default |
| Full Docker startup | Complete | `docker compose up --build` |

All contract paths in the table are mounted below `/api/v1`.
The frontend uses the public localhost URL in the browser and the Compose
service URL during server rendering, so both client-side mutations and dynamic
result pages reach the same backend.

## Verification

Run the same gates used for the integration handoff:

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

`backend/tests/test_end_to_end_workflow.py` is the executable acceptance test
for the complete public workflow path.

## Current MVP limits

- Workflow, report, marketing, and watcher data are stored in memory and reset
  when the backend restarts.
- The mock provider is deterministic and intended for development and tests.
- The OpenAI adapter is opt-in only: set `AI_PROVIDER=openai`,
  `AI_PRIMARY_MODEL`, and `OPENAI_API_KEY` deliberately to enable it.
- Production authentication, durable database migrations, deployment secrets,
  and production observability remain outside this MVP foundation.
