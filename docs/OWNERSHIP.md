# Team ownership and starting points

Shared rule: changes to `backend/app/schemas`, `frontend/lib/types.ts`, or published endpoint shapes require a short team review because they affect everyone.

## Person 1 — backend lead, orchestrator, management

Owns:

- `backend/app/api/workflows.py`
- `backend/app/agents/orchestrator.py`
- `backend/app/agents/manager.py`
- `backend/app/services/ai_service.py`
- `backend/app/services/workflow_service.py`
- workflow and task schemas

Start with: replace `MockAIProvider` behind the existing `AIService` protocol and extend `WorkflowService.run` into the workflow state machine. Keep provider calls out of routers and agents.

First handoff: keep `POST /api/v1/workflows`, `GET /api/v1/workflows/{id}`, and `GET /api/v1/workflows/{id}/tasks` compatible with the frontend types.

## Person 2 — workers, reports, prediction

Owns:

- `backend/app/agents/worker.py`
- `backend/app/agents/report_agent.py`
- `backend/app/services/worker_service.py`
- `backend/app/services/prediction_service.py`
- `backend/app/api/reports.py`
- worker and report schemas
- `backend/data/`

Start with: add deterministic worker profiles and matching, then create a small versioned sales dataset and prediction service. Expose report data through the existing report router.

First handoff: return a `Report` matching both the Pydantic and TypeScript contracts.

## Person 3 — marketing, watcher, reliability, Docker

Owns:

- `backend/app/agents/marketing_agent.py`
- `backend/app/agents/watcher.py`
- `backend/app/services/marketing_service.py`
- `backend/app/services/watcher_service.py`
- `backend/app/api/marketing.py`
- `backend/app/api/watcher.py`
- marketing and watcher schemas
- Docker files

Start with: implement event recording and the retry wrapper, then connect marketing generation. Preserve the Python budget check in `MarketingPlan.validate_budget`.

First handoff: make failure, retry, and recovery events visible through `/api/v1/watcher`.

## Person 4 — command center and workflow UI

Owns:

- `frontend/app/page.tsx`
- `frontend/app/workflows/[id]/page.tsx`
- `frontend/components/ExecutiveObjectiveForm.tsx`
- `frontend/components/WorkflowPipeline.tsx`
- `frontend/components/TaskCard.tsx`
- `frontend/lib/api.ts`
- workflow and task TypeScript types

Start with: extend the working create-and-view flow, add polling for stage changes, and render worker assignment reasons.

First handoff: coordinate schema changes with Person 1, never infer business state in the browser.

## Person 5 — reports, marketing, watcher UI

Owns:

- `frontend/app/reports/[id]/page.tsx`
- `frontend/app/marketing/[id]/page.tsx`
- `frontend/app/watcher/page.tsx`
- `frontend/components/FinancialSummary.tsx`
- `frontend/components/BudgetEditor.tsx`
- `frontend/components/WatcherPanel.tsx`
- report, marketing, and watcher TypeScript types

Start with: replace the typed empty states with report cards, a prediction chart, an editable budget, and the watcher event log.

First handoff: coordinate with Persons 2 and 3 and keep backend validation authoritative.

## Merge order

1. Shared schema change, reviewed first.
2. Backend implementation and endpoint test.
3. Frontend API adapter and UI.
4. Full Compose smoke test.

