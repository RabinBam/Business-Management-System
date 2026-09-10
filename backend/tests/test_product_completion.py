import asyncio
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import SQLiteJsonStore
from app.main import app
from app.schemas.marketing import BudgetAllocation, MarketingPlan
from app.schemas.report import FinancialSummary, Report, SalesPrediction
from app.schemas.task import ManagementReview, TaskRead
from app.schemas.worker import WorkerResult
from app.schemas.workflow import WorkflowCreate, WorkflowRead, WorkflowStatus
from app.services.ai_service import MockAIProvider
from app.services.marketing_service import MarketingService, marketing_service
from app.services.report_service import ReportService, get_report_service
from app.services.watcher_service import WatcherService, watcher_service
from app.services.workflow_service import (
    WorkflowCollaborators,
    WorkflowService,
    get_workflow_service,
)


def _payload() -> WorkflowCreate:
    return WorkflowCreate(
        title="Product completion",
        objective="Complete and verify every production handoff safely.",
        budget=100_000,
        deadline=date.today() + timedelta(days=30),
    )


@pytest.fixture(autouse=True)
def clear_application_state() -> None:
    get_workflow_service().clear()
    get_report_service().clear()
    marketing_service.clear()
    watcher_service.clear()
    yield
    get_workflow_service().clear()
    get_report_service().clear()
    marketing_service.clear()
    watcher_service.clear()


def test_sqlite_services_restore_validated_state() -> None:
    store = SQLiteJsonStore("sqlite:///:memory:")
    workflow_service = WorkflowService(ai_service=MockAIProvider(), store=store)
    created = workflow_service.create(_payload())

    restored = WorkflowService(ai_service=MockAIProvider(), store=store)
    assert restored.require(created.id).title == created.title

    report_service = ReportService(store=store)
    report_service.generate_report(created, task_spend=25_000)
    assert ReportService(store=store).get_report(created.id) is not None

    marketing = MarketingPlan(
        workflow_id=created.id,
        approved_budget=75_000,
        objective=created.objective,
        target_audience="Operations leaders",
        allocations=[BudgetAllocation(channel="Search", amount=10_000, reason="High intent")],
        timeline=["Week 1: launch"],
    )
    marketing_service_store = MarketingService(store=store)
    marketing_service_store.save_plan(marketing)
    assert MarketingService(store=store).get_plan(created.id) is not None

    watcher = WatcherService(store=store)
    watcher.record_event(
        workflow_id=created.id,
        component="test",
        event_type="RECOVERED",
        message="State restored",
        resolved=True,
    )
    assert len(WatcherService(store=store).status().events) == 1

    report_service.prune_orphans(set())
    marketing_service_store.prune_orphans(set())
    watcher.prune_orphans(set())
    assert report_service.get_report(created.id) is None
    assert marketing_service_store.get_plan(created.id) is None
    assert watcher.status().events == []
    store.close()


def test_management_revision_reexecutes_and_then_completes() -> None:
    reviews = [
        {
            "task_id": "task-001",
            "decision": "REVISION_REQUIRED",
            "feedback": "Add measurable evidence.",
            "revision_instructions": ["Attach measurable evidence"],
        },
        {
            "task_id": "task-002",
            "decision": "APPROVED",
            "feedback": "Accepted.",
        },
        {
            "task_id": "task-001",
            "decision": "APPROVED",
            "feedback": "Revision accepted.",
        },
        {
            "task_id": "task-002",
            "decision": "APPROVED",
            "feedback": "Accepted.",
        },
    ]
    provider = MockAIProvider({ManagementReview: reviews})
    executions = 0

    def execute(tasks: list[TaskRead]) -> list[WorkerResult]:
        nonlocal executions
        executions += 1
        return [
            WorkerResult(
                task_id=task.id,
                worker_id="w-001",
                summary="Completed with evidence.",
                cost=task.estimated_cost,
            )
            for task in tasks
        ]

    def report(
        workflow: WorkflowRead,
        _tasks: list[TaskRead],
        results: list[WorkerResult],
        _reviews: list[ManagementReview],
    ) -> Report:
        spend = sum(result.cost for result in results)
        return Report(
            workflow_id=workflow.id,
            financial=FinancialSummary(
                total_budget=workflow.budget,
                planned_spend=spend,
                remaining_budget=workflow.budget - spend,
            ),
            sales_prediction=SalesPrediction(
                current_sales=100,
                predicted_sales=110,
                growth_percent=10,
            ),
        )

    def marketing(workflow: WorkflowRead, report: Report) -> MarketingPlan:
        return MarketingPlan(
            workflow_id=workflow.id,
            approved_budget=report.financial.remaining_budget,
            objective=workflow.objective,
            target_audience="Operations leaders",
        )

    service = WorkflowService(
        ai_service=provider,
        collaborators=WorkflowCollaborators(
            execute_workers=execute,
            generate_report=report,
            generate_marketing=marketing,
        ),
    )
    workflow = service.create(_payload())
    completed = asyncio.run(service.run_workflow(workflow.id))

    assert completed.status is WorkflowStatus.MARKETING
    asyncio.run(
        service.save_marketing_draft(
            workflow.id,
            service._artifacts[workflow.id].marketing,
            approve=True,
        )
    )
    completed = asyncio.run(service.run_workflow(workflow.id))
    assert completed.status is WorkflowStatus.COMPLETED
    assert executions == 2
    tasks = service.get_tasks(workflow.id) or []
    assert tasks[0].revision_count == 1
    assert tasks[0].revision_instructions == ["Attach measurable evidence"]


def test_completed_public_product_contracts() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v1/workflows",
        json=_payload().model_dump(mode="json"),
    )
    workflow_id = created.json()["data"]["id"]

    refined = client.post(f"/api/v1/workflows/{workflow_id}/refine")
    completed = client.post(f"/api/v1/workflows/{workflow_id}/run")
    assert completed.json()["data"]["status"] == "MARKETING"
    plan = client.get(f"/api/v1/workflows/{workflow_id}/marketing").json()["data"]
    assert (
        client.post(f"/api/v1/workflows/{workflow_id}/marketing/approve", json=plan).status_code
        == 200
    )
    completed = client.post(f"/api/v1/workflows/{workflow_id}/run")
    status_response = client.get(f"/api/v1/workflows/{workflow_id}/status")
    workflows = client.get("/api/v1/workflows")
    results = client.get(f"/api/v1/workflows/{workflow_id}/results")
    reviews = client.get(f"/api/v1/workflows/{workflow_id}/reviews")
    workers = client.get("/api/v1/workers")
    dashboard = client.get("/api/v1/dashboard")
    report = client.get(f"/api/v1/workflows/{workflow_id}/report")

    assert refined.json()["data"]["status"] == "EXECUTING"
    assert completed.json()["data"]["status"] == "COMPLETED"
    assert status_response.json()["data"]["status"] == "COMPLETED"
    assert len(workflows.json()["data"]) == 1
    assert len(results.json()["data"]) == 2
    assert len(reviews.json()["data"]) == 2
    assert len(workers.json()["data"]) >= 1
    assert dashboard.json()["data"]["metrics"]["completed_workflows"] == 1
    assert report.json()["data"]["financial"]["planned_spend"] > 0
    assert "x-request-id" in dashboard.headers
    assert dashboard.headers["x-content-type-options"] == "nosniff"


def test_request_guard_rejects_oversized_payloads() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/workflows",
        content=b"{}",
        headers={"Content-Length": "1000001", "Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "REQUEST_TOO_LARGE"
    assert response.headers["x-frame-options"] == "DENY"


def test_delete_cascades_across_product_services() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/v1/workflows",
        json=_payload().model_dump(mode="json"),
    )
    workflow_id = created.json()["data"]["id"]
    assert client.post(f"/api/v1/workflows/{workflow_id}/run").status_code == 200
    assert client.get(f"/api/v1/workflows/{workflow_id}/report").status_code == 200
    assert client.get(f"/api/v1/workflows/{workflow_id}/marketing").status_code == 200

    deleted = client.delete(f"/api/v1/workflows/{workflow_id}")

    assert deleted.status_code == 204
    assert client.get(f"/api/v1/workflows/{workflow_id}").status_code == 404
    assert client.get(f"/api/v1/workflows/{workflow_id}/report").status_code == 404
    assert client.get(f"/api/v1/workflows/{workflow_id}/marketing").status_code == 404
    assert all(
        event["workflow_id"] != workflow_id
        for event in client.get("/api/v1/watcher/events").json()["data"]
    )
