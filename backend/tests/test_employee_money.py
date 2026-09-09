import asyncio
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import SQLiteJsonStore, get_json_store
from app.main import app
from app.schemas.task import ManagementReview, TaskStatus
from app.schemas.workflow import WorkflowCreate
from app.services.ai_service import MockAIProvider
from app.services.report_service import ReportService
from app.services.workflow_service import WorkflowService, get_workflow_service


@pytest.fixture
def client():
    get_workflow_service().clear()
    get_json_store().clear_namespace("money")
    with TestClient(app) as c:
        yield c
    get_workflow_service().clear()
    get_json_store().clear_namespace("money")


def payload(**extra):
    return {
        "title": "Employee delivery",
        "objective": "Prepare a real written delivery plan.",
        "budget": 1001.01,
        "deadline": (date.today() + timedelta(days=15)).isoformat(),
        "execution_mode": "employee",
        **extra,
    }


def test_employee_submission_review_and_persistence(client):
    created = client.post("/api/v1/workflows", json=payload()).json()["data"]
    wid = created["id"]
    assert client.post(f"/api/v1/workflows/{wid}/refine").status_code == 200
    tasks = client.get(f"/api/v1/workflows/{wid}/tasks").json()["data"]
    assert all(t["assigned_worker_id"] for t in tasks)
    assert round(sum(t["estimated_cost"] for t in tasks), 2) <= created["budget"] * 0.6
    waiting = client.post(f"/api/v1/workflows/{wid}/run").json()["data"]
    assert waiting["status"] == "EXECUTING"
    t = tasks[0]
    wrong = "w-001" if t["assigned_worker_id"] != "w-001" else "w-002"
    path = f"/api/v1/employees/{t['assigned_worker_id']}/tasks/{wid}/{t['id']}/submit"
    assert (
        client.post(
            path.replace(t["assigned_worker_id"], wrong),
            json={"deliverable": "A complete written plan."},
        ).status_code
        == 409
    )
    assert client.post(path, json={"deliverable": "              "}).status_code == 422
    dependent = tasks[1]
    dep_path = (
        f"/api/v1/employees/{dependent['assigned_worker_id']}/tasks/{wid}/{dependent['id']}/submit"
    )
    assert (
        client.post(dep_path, json={"deliverable": "A complete written plan."}).status_code == 409
    )
    for task in tasks:
        url = f"/api/v1/employees/{task['assigned_worker_id']}/tasks/{wid}/{task['id']}/submit"
        assert (
            client.post(
                url,
                json={"deliverable": "Scope, milestones and controls are documented in this plan."},
            ).status_code
            == 200
        )
        assert client.post(url, json={"deliverable": "Duplicate submission."}).status_code == 409
    submitted = client.get(f"/api/v1/workflows/{wid}/tasks").json()["data"]
    assert {t["status"] for t in submitted} == {"SUBMITTED"}
    restored = WorkflowService(ai_service=MockAIProvider(), store=get_json_store())
    assert len(restored.get_worker_results(wid)) == len(tasks)
    completed = client.post(f"/api/v1/workflows/{wid}/run")
    assert completed.json()["data"]["status"] == "COMPLETED"
    assert all(
        t["status"] == "COMPLETED"
        for t in client.get(f"/api/v1/workflows/{wid}/tasks").json()["data"]
    )
    assert client.get(f"/api/v1/employees/{t['assigned_worker_id']}/tasks").status_code == 200


def test_employee_revision_keeps_other_submissions():
    provider = MockAIProvider(
        {
            ManagementReview: [
                {
                    "task_id": "task-001",
                    "decision": "REVISION_REQUIRED",
                    "feedback": "Add evidence",
                    "revision_instructions": ["Add evidence"],
                },
                {"task_id": "task-002", "decision": "APPROVED", "feedback": "Accepted"},
            ]
        }
    )
    service = WorkflowService(ai_service=provider, store=SQLiteJsonStore("sqlite:///:memory:"))
    workflow = service.create(WorkflowCreate(**payload()))

    async def check():
        await service.prepare_workflow(workflow.id)
        for t in service.get_tasks(workflow.id):
            await service.submit_employee_work(
                workflow.id, t.id, t.assigned_worker_id, "Written work with milestones."
            )
        result = await service.run_workflow(workflow.id)
        assert result.status == "EXECUTING"
        assert [r.task_id for r in service.get_worker_results(workflow.id)] == ["task-002"]
        assert service.get_tasks(workflow.id)[0].status == TaskStatus.PENDING
        assert service.get_tasks(workflow.id)[1].status == TaskStatus.COMPLETED

    asyncio.run(check())


def test_money_is_empty_and_uses_exact_decimal_totals(client):
    assert client.get("/api/v1/money").json()["data"]["entries"] == []
    for amount in ["0.10", "0.20"]:
        r = client.post(
            "/api/v1/money",
            json={
                "kind": "income",
                "amount": amount,
                "description": "Sales received",
                "date": date.today().isoformat(),
            },
        )
        assert r.status_code == 201
    assert client.get("/api/v1/money").json()["data"]["income"] == "0.30"
    bad = {
        "kind": "expense",
        "amount": "-1",
        "description": "Invalid cost",
        "date": date.today().isoformat(),
    }
    assert client.post("/api/v1/money", json=bad).status_code == 422
    bad["amount"] = "1.001"
    assert client.post("/api/v1/money", json=bad).status_code == 422


def test_prediction_uses_only_supplied_monthly_history():
    workflow = WorkflowCreate(**payload(sales_history=[100, 200, 300]))
    service = WorkflowService(ai_service=MockAIProvider())
    report = ReportService().generate_report(service.create(workflow))
    assert report.sales_prediction.predicted_sales == 400
    assert report.sales_prediction.method == "user_monthly_history"


def test_marketing_decimal_budget_boundary():
    from app.schemas.marketing import BudgetAllocation, MarketingPlan

    plan = MarketingPlan(
        workflow_id="boundary",
        approved_budget=0.3,
        objective="Test",
        target_audience="Test",
        allocations=[
            BudgetAllocation(channel="One", amount=0.1, reason="Test"),
            BudgetAllocation(channel="Two", amount=0.2, reason="Test"),
        ],
    )
    assert plan.validate_budget() == 0.3


def test_demo_completion(client):
    w = client.post("/api/v1/workflows", json=payload()).json()["data"]
    client.post(f"/api/v1/workflows/{w['id']}/refine")
    result = client.post("/api/v1/employees/demo/quick-complete")
    assert result.status_code == 200
    assert result.json()["data"][0]["status"] == "REPORTING"
    tasks = client.get(f"/api/v1/workflows/{w['id']}/tasks").json()["data"]
    assert all(t["status"] == "COMPLETED" for t in tasks)
    assert client.post("/api/v1/employees/demo/quick-complete").json()["data"] == []


def test_demo_reset_backups_and_preserves_other_data(tmp_path):
    import sqlite3

    from app.demo_start import reset_demo
    path = tmp_path / "demo.db"
    store = SQLiteJsonStore("sqlite:///" + str(path))
    store.put("workflows", "demo", {"title": "demo"})
    store.put("money", "entry", {"amount": "12"})
    store.put("employees", "employee", {"name": "kept"})
    reset_demo(path)
    assert store.get("workflows", "demo") is None
    assert store.get("money", "entry") is None
    assert store.get("employees", "employee") == {"name": "kept"}
    backups = list(tmp_path.glob("byapari-before-launch-*.db"))
    assert len(backups) == 1
    with sqlite3.connect(backups[0]) as connection:
        assert connection.execute("SELECT count(*) FROM json_records").fetchone()[0] == 3
