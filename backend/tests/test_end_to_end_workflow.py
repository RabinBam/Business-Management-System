from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.marketing_service import marketing_service
from app.services.watcher_service import watcher_service
from app.services.workflow_service import get_workflow_service


@pytest.fixture(autouse=True)
def reset_runtime_state() -> None:
    """Keep the singleton-backed acceptance path deterministic and isolated."""

    get_workflow_service().clear()
    marketing_service.clear()
    watcher_service.clear()
    yield
    get_workflow_service().clear()
    marketing_service.clear()
    watcher_service.clear()


def test_dev_acceptance_workflow_reaches_every_handoff() -> None:
    """Exercise the complete DEV guide path through the public HTTP contracts."""

    payload = {
        "title": "DEV acceptance launch",
        "objective": "Launch a measurable operating plan with approved handoffs.",
        "budget": 500_000,
        "deadline": (date.today() + timedelta(days=30)).isoformat(),
    }

    with TestClient(app) as client:
        docs = client.get("/docs")
        openapi = client.get("/openapi.json")
        assert docs.status_code == 200
        assert openapi.status_code == 200
        assert "/api/v1/workflows" in openapi.json()["paths"]

        created = client.post("/api/v1/workflows", json=payload)
        assert created.status_code == 201
        workflow_id = created.json()["data"]["id"]

        completed = client.post(f"/api/v1/workflows/{workflow_id}/run")
        assert completed.json()["data"]["status"] == "MARKETING"
        plan = client.get(f"/api/v1/workflows/{workflow_id}/marketing").json()["data"]
        assert (
            client.post(f"/api/v1/workflows/{workflow_id}/marketing/approve", json=plan).status_code
            == 200
        )
        completed = client.post(f"/api/v1/workflows/{workflow_id}/run")
        assert completed.status_code == 200
        completed_workflow = completed.json()["data"]
        assert completed_workflow["status"] == "COMPLETED"
        assert completed_workflow["current_stage"] == "completed"
        assert completed_workflow["completed_at"] is not None
        assert completed_workflow["executive_summary"]["management_recommendation"]

        loaded = client.get(f"/api/v1/workflows/{workflow_id}")
        tasks = client.get(f"/api/v1/workflows/{workflow_id}/tasks")
        report = client.get(f"/api/v1/workflows/{workflow_id}/reports")
        marketing = client.get(f"/api/v1/workflows/{workflow_id}/marketing")
        watcher = client.get("/api/v1/watcher/status")

    assert loaded.status_code == 200
    assert loaded.json()["data"] == completed_workflow

    task_data = tasks.json()["data"]
    assert tasks.status_code == 200
    assert len(task_data) >= 1
    assert {task["status"] for task in task_data} == {"COMPLETED"}

    report_data = report.json()["data"]
    assert report.status_code == 200
    assert report_data["workflow_id"] == workflow_id
    assert report_data["financial"]["total_budget"] == payload["budget"]

    marketing_data = marketing.json()["data"]
    assert marketing.status_code == 200
    assert marketing_data["workflow_id"] == workflow_id
    assert (
        sum(item["amount"] for item in marketing_data["allocations"])
        <= (marketing_data["approved_budget"])
    )

    watcher_data = watcher.json()["data"]
    assert watcher.status_code == 200
    assert watcher_data["state"] == "IDLE"
    assert watcher_data["active_incidents"] == 0
    lifecycle_events = [
        event
        for event in watcher_data["events"]
        if event["workflow_id"] == workflow_id and event["event_type"] == "STATUS_CHANGED"
    ]
    assert len(lifecycle_events) == 8
    assert all(event["resolved"] for event in lifecycle_events)
