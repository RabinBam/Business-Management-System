"""Tests for the report service — financial arithmetic, risks, and recommendations."""

from datetime import date, timedelta

from app.schemas.report import Report, SalesPrediction
from app.schemas.workflow import WorkflowRead
from app.services.report_service import ReportService


def _make_workflow(**overrides: object) -> WorkflowRead:
    defaults: dict[str, object] = {
        "id": "wf-test001",
        "title": "Test workflow",
        "objective": "Run the report service tests successfully.",
        "budget": 100_000.0,
        "deadline": date.today() + timedelta(days=30),
    }
    defaults.update(overrides)
    return WorkflowRead(**defaults)  # type: ignore[arg-type]


class TestReportGeneration:
    """Verify report assembly and caching."""

    def test_generate_report_returns_schema(self) -> None:
        service = ReportService()
        workflow = _make_workflow()
        report = service.generate_report(workflow)
        assert isinstance(report, Report)
        assert report.workflow_id == "wf-test001"

    def test_financial_summary_arithmetic(self) -> None:
        service = ReportService()
        workflow = _make_workflow(budget=200_000.0)
        report = service.generate_report(workflow, task_spend=50_000.0)
        assert report.financial.total_budget == 200_000.0
        assert report.financial.planned_spend == 50_000.0
        assert report.financial.remaining_budget == 150_000.0

    def test_prediction_is_populated(self) -> None:
        service = ReportService()
        workflow = _make_workflow()
        report = service.generate_report(workflow)
        assert isinstance(report.sales_prediction, SalesPrediction)
        assert report.sales_prediction.method == "linear_regression"

    def test_report_is_cached(self) -> None:
        service = ReportService()
        workflow = _make_workflow()
        report_1 = service.generate_report(workflow)
        report_2 = service.get_report(workflow.id)
        assert report_2 is not None
        assert report_1.workflow_id == report_2.workflow_id

    def test_get_report_returns_none_when_missing(self) -> None:
        service = ReportService()
        assert service.get_report("wf-nonexistent") is None


class TestRiskAssessment:
    """Verify deterministic risk identification."""

    def test_overspend_risk(self) -> None:
        service = ReportService()
        workflow = _make_workflow(budget=100.0)
        report = service.generate_report(workflow, task_spend=200.0)
        assert any("exceeds" in r.lower() for r in report.risks)

    def test_low_remaining_budget_risk(self) -> None:
        service = ReportService()
        workflow = _make_workflow(budget=100.0)
        report = service.generate_report(workflow, task_spend=95.0)
        assert any("10%" in r or "remains" in r.lower() for r in report.risks)


class TestRecommendations:
    """Verify deterministic recommendations."""

    def test_low_utilisation_recommendation(self) -> None:
        service = ReportService()
        workflow = _make_workflow(budget=100_000.0)
        report = service.generate_report(workflow, task_spend=10_000.0)
        assert any("utilisation" in r.lower() for r in report.recommendations)

    def test_has_at_least_one_recommendation(self) -> None:
        service = ReportService()
        workflow = _make_workflow()
        report = service.generate_report(workflow)
        assert len(report.recommendations) >= 1


class TestReportEndpoint:
    """Integration test through the FastAPI test client."""

    def test_report_for_existing_workflow(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        payload = {
            "title": "Report test",
            "objective": "Verify that the report endpoint works end to end.",
            "budget": 50_000,
            "deadline": (date.today() + timedelta(days=14)).isoformat(),
        }
        created = client.post("/api/v1/workflows", json=payload)
        assert created.status_code == 201
        workflow_id = created.json()["data"]["id"]

        response = client.get(f"/api/v1/workflows/{workflow_id}/report")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["workflow_id"] == workflow_id
        assert "financial" in body["data"]
        assert "sales_prediction" in body["data"]

    def test_report_for_missing_workflow(self) -> None:
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        response = client.get("/api/v1/workflows/wf-ghost/report")
        assert response.status_code == 404
