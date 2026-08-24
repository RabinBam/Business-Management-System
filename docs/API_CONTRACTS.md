# API contracts

Base URL: `/api/v1`

All successful responses use:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed"
}
```

All handled failures use:

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Readable error"
  }
}
```

## Foundation endpoints

| Method | Path | Owner | Purpose |
| --- | --- | --- | --- |
| `GET` | `/health` | P1 | Container and service health |
| `POST` | `/api/v1/workflows` | P1 | Create one executive workflow |
| `GET` | `/api/v1/workflows` | P1 | List workflows, newest first |
| `GET` | `/api/v1/workflows/{id}` | P1 | Read status and current stage |
| `GET` | `/api/v1/workflows/{id}/status` | P1 | Read lightweight lifecycle status |
| `POST` | `/api/v1/workflows/{id}/refine` | P1 | Segment and refine tasks without executing |
| `POST` | `/api/v1/workflows/{id}/run` | P1 | Begin the orchestration pipeline |
| `POST` | `/api/v1/workflows/{id}/retry` | P1 | Reset a failed workflow for retry |
| `POST` | `/api/v1/workflows/{id}/cancel` | P1 | Cancel a non-terminal workflow |
| `DELETE` | `/api/v1/workflows/{id}` | P1 | Delete a workflow; admin-key protected when configured |
| `GET` | `/api/v1/workflows/{id}/tasks` | P1/P2 | Read decomposed and assigned tasks |
| `GET` | `/api/v1/workflows/{id}/results` | P1/P2 | Read validated worker outputs and costs |
| `GET` | `/api/v1/workflows/{id}/reviews` | P1 | Read management decisions and revision instructions |
| `GET` | `/api/v1/workers` | P2 | Read live worker directory and workload |
| `GET` | `/api/v1/workers/{id}` | P2 | Read one worker |
| `GET` | `/api/v1/dashboard` | P1/P4 | Read portfolio metrics, recent workflows, and events |
| `GET` | `/api/v1/workflows/{id}/report` | P2 | Read financial and prediction report |
| `GET` | `/api/v1/workflows/{id}/marketing` | P3 | Read marketing plan |
| `PUT` | `/api/v1/workflows/{id}/marketing` | P3 | Save human-edited plan |
| `GET` | `/api/v1/watcher` | P3 | Read state and recent events |
| `GET` | `/api/v1/watcher/status` | P3 | Status alias from the developer guide |
| `GET` | `/api/v1/watcher/events` | P3 | Read the event collection only |

## Status values

Workflow: `CREATED`, `SEGMENTING`, `ASSIGNING`, `EXECUTING`, `REVIEWING`, `REPORTING`, `MARKETING`, `FINAL_REVIEW`, `COMPLETED`, `FAILED`, `CANCELLED`.

Task: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`.

The source of truth is `backend/app/schemas`; `frontend/lib/types.ts` mirrors it.
