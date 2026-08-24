# Product implementation status

This file records the repository status against the supplied `DEV.md` build and handoff checklist.

## End-to-end product path

The default `AI_PROVIDER=mock` path is credential-free and deterministic:

1. An executive creates a validated workflow.
2. The orchestrator segments the objective and management refines the task plan.
3. Difficulty-weighted cost estimates are allocated inside the approved budget.
4. Workers are matched deterministically by role, experience, skills, and stable tie-breaking.
5. Management reviews every result. Revision requests requeue work with explicit instructions, up to the configured limit.
6. The report service records real task spend and a validated sales prediction.
7. Marketing uses approved report context and enforces its budget again in Python.
8. Management creates the final executive summary and completes the workflow.
9. Workflow, tasks, artifacts, reports, plans, and watcher events persist in SQLite across restarts.

## Completed handoffs

| Area | Product behavior |
| --- | --- |
| Workflow management | Create, list, read, refine, run, retry, cancel, delete, status, tasks, results, and reviews |
| Orchestration | Guarded state transitions, per-workflow run locks, transient recovery, bounded revision loop, and failure records |
| AI provider boundary | Provider calls stay behind `AIService`; mock is default and OpenAI is explicit opt-in |
| Workforce | Profile directory, deterministic matching, assignments, workload, validated outputs, and evidence |
| Finance and reports | Task costs flow into spend, prediction results are validated, and live PDF export is available |
| Marketing | Generated and editable plans with authoritative backend budget validation |
| Reliability | Watcher events, retries, recovery visibility, request IDs, request limits, rate limits, and security headers |
| Command center | Live portfolio KPIs, latest workflow pipeline, and operational event feed |
| Persistence | Thread-safe SQLite JSON repository and a durable Docker volume |
| Delivery | Backend tests, Ruff, frontend lint/typecheck/build/audit, Docker build, and CI on `dev`/`main`/`master` |

All API paths are mounted below `/api/v1`; see [API_CONTRACTS.md](API_CONTRACTS.md).

## Provider and secret safety

No OpenAI or Hugging Face token is checked in or required. The OpenAI adapter is activated only when all of the following are set deliberately:

```text
AI_PROVIDER=openai
AI_PRIMARY_MODEL=<model>
OPENAI_API_KEY=<secret supplied by deployment platform>
```

The application fails configuration clearly instead of silently falling back to a billable provider. Shared deployments should also configure `ADMIN_API_KEY`, `TRUSTED_HOSTS`, and `FRONTEND_ORIGIN`, and should run behind an identity-aware proxy.

## Verification

```bash
cd backend
ruff check .
pytest

cd ../frontend
npm audit --audit-level=high
npm run check

cd ..
docker compose -f docker-compose.yml config --quiet
docker compose -f docker-compose.yml build
```

The main product acceptance coverage is in `backend/tests/test_end_to_end_workflow.py` and `backend/tests/test_product_completion.py`.
