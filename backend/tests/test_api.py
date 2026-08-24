from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _workflow_payload() -> dict[str, object]:
    return {
        "title": "Product launch",
        "objective": "Launch a new product with an accountable operating plan.",
        "budget": 500_000,
        "deadline": (date.today() + timedelta(days=30)).isoformat(),
    }


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_read_and_run_workflow() -> None:
    created = client.post("/api/v1/workflows", json=_workflow_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["success"] is True
    workflow_id = body["data"]["id"]

    loaded = client.get(f"/api/v1/workflows/{workflow_id}")
    assert loaded.status_code == 200
    assert loaded.json()["data"]["status"] == "CREATED"

    started = client.post(f"/api/v1/workflows/{workflow_id}/run")
    assert started.status_code == 200
    assert started.json()["data"]["status"] == "COMPLETED"
    assert started.json()["data"]["executive_summary"] is not None

    tasks = client.get(f"/api/v1/workflows/{workflow_id}/tasks")
    assert tasks.status_code == 200
    assert len(tasks.json()["data"]) == 2
    assert {task["status"] for task in tasks.json()["data"]} == {"COMPLETED"}


def test_marketing_budget_is_validated() -> None:
    response = client.put(
        "/api/v1/workflows/wf-test/marketing",
        json={
            "workflow_id": "wf-test",
            "approved_budget": 100,
            "objective": "Reach qualified buyers",
            "target_audience": "Operations leaders",
            "allocations": [
                {"channel": "Search", "amount": 120, "reason": "High intent"}
            ],
            "timeline": ["Week 1: launch"],
        },
    )
    assert response.status_code == 422


def test_watcher_starts_idle() -> None:
    response = client.get("/api/v1/watcher")
    assert response.status_code == 200
    assert response.json()["data"]["state"] == "IDLE"


def test_missing_resource_uses_shared_error_envelope() -> None:
    response = client.get("/api/v1/workflows/wf-missing")
    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {
            "code": "WORKFLOW_NOT_FOUND",
            "message": "Workflow 'wf-missing' was not found.",
        },
    }


def test_dev_guide_report_and_marketing_endpoints() -> None:
    created = client.post("/api/v1/workflows", json=_workflow_payload())
    workflow_id = created.json()["data"]["id"]
    completed = client.post(f"/api/v1/workflows/{workflow_id}/run")
    assert completed.json()["data"]["status"] == "COMPLETED"

    report = client.get(f"/api/v1/workflows/{workflow_id}/reports")
    regenerated = client.post(f"/api/v1/workflows/{workflow_id}/reports/generate")
    marketing = client.post(f"/api/v1/workflows/{workflow_id}/marketing/generate")

    assert report.status_code == 200
    assert regenerated.status_code == 200
    assert marketing.status_code == 200
