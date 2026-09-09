"""Person 2 starting point for financial arithmetic and report assembly."""

from __future__ import annotations

from threading import RLock

from app.database import SQLiteJsonStore, get_json_store
from app.schemas.report import FinancialSummary, Report, SalesPrediction
from app.schemas.workflow import WorkflowRead
from app.services.prediction_service import PredictionService


class ReportService:
    """Assemble deterministic financial data into the shared Report schema.

    All arithmetic lives here, not in the router or the agent. The agent may
    later add a narrative layer on top, but numbers are always computed by
    this service so they remain auditable.
    """

    def __init__(self, *, store: SQLiteJsonStore | None = None) -> None:
        self._reports: dict[str, Report] = {}
        self._store = store
        self._lock = RLock()
        if store is not None:
            self._reports = {
                workflow_id: Report.model_validate(payload)
                for workflow_id, payload in store.list("reports")
            }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_report(
        self,
        workflow: WorkflowRead,
        task_spend: float = 0.0,
    ) -> Report:
        """Build a report for *workflow*, cache it, and return it.

        Parameters
        ----------
        workflow:
            The workflow to report on.  ``budget`` is read from here.
        task_spend:
            Cumulative planned spend across all completed tasks.  Defaults
            to zero when tasks have not yet been costed.
        """
        financial = self._build_financial_summary(
            total_budget=workflow.budget,
            planned_spend=task_spend,
        )

        prediction = self._build_sales_prediction(workflow.sales_history)

        risks = self._assess_risks(financial, prediction)
        recommendations = self._build_recommendations(financial, prediction)

        report = Report(
            workflow_id=workflow.id,
            financial=financial,
            sales_prediction=prediction,
            risks=risks,
            recommendations=recommendations,
        )
        with self._lock:
            self._reports[workflow.id] = report
            if self._store is not None:
                self._store.put(
                    "reports",
                    workflow.id,
                    report.model_dump(mode="json"),
                )
        return report.model_copy(deep=True)

    def get_report(self, workflow_id: str) -> Report | None:
        """Return a previously generated report, or ``None``."""
        with self._lock:
            report = self._reports.get(workflow_id)
            return report.model_copy(deep=True) if report is not None else None

    def list_reports(self) -> list[Report]:
        with self._lock:
            return [report.model_copy(deep=True) for report in self._reports.values()]

    def delete_report(self, workflow_id: str) -> None:
        with self._lock:
            self._reports.pop(workflow_id, None)
            if self._store is not None:
                self._store.delete("reports", workflow_id)

    def prune_orphans(self, valid_workflow_ids: set[str]) -> None:
        with self._lock:
            orphans = set(self._reports) - valid_workflow_ids
        for workflow_id in orphans:
            self.delete_report(workflow_id)

    def clear(self) -> None:
        with self._lock:
            self._reports.clear()
            if self._store is not None:
                self._store.clear_namespace("reports")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_financial_summary(
        *,
        total_budget: float,
        planned_spend: float,
    ) -> FinancialSummary:
        return FinancialSummary(
            total_budget=total_budget,
            planned_spend=planned_spend,
            remaining_budget=total_budget - planned_spend,
        )

    @staticmethod
    def _build_sales_prediction(history: list[float]) -> SalesPrediction:
        if len(history) < 2:
            return SalesPrediction(
                current_sales=history[-1] if history else 0,
                predicted_sales=0,
                growth_percent=0,
                method="unavailable",
            )
        slope, intercept = PredictionService._linear_regression(history)
        predicted = max(0, slope * len(history) + intercept)
        latest = history[-1]
        return SalesPrediction(
            current_sales=latest,
            predicted_sales=round(predicted, 2),
            growth_percent=round((predicted - latest) / latest * 100, 2) if latest else 0,
            method="user_monthly_history",
        )

    @staticmethod
    def _assess_risks(
        financial: FinancialSummary,
        prediction: SalesPrediction,
    ) -> list[str]:
        risks: list[str] = []

        if financial.remaining_budget < 0:
            risks.append(
                f"Planned spend exceeds total budget by ${abs(financial.remaining_budget):,.2f}."
            )
        elif financial.remaining_budget < financial.total_budget * 0.10:
            risks.append("Less than 10% of budget remains — limited room for unplanned expenses.")

        if prediction.method == "unavailable":
            risks.append("Sales forecast unavailable: provide at least two monthly revenue values.")
        elif prediction.growth_percent < 0:
            risks.append(
                f"Sales are projected to decline by {abs(prediction.growth_percent):.1f}%."
            )
        elif prediction.growth_percent < 5:
            risks.append(
                "Projected sales growth is below 5% — consider reviewing "
                "demand-generation strategy."
            )

        if not risks:
            risks.append("No significant risks identified at this stage.")

        return risks

    @staticmethod
    def _build_recommendations(
        financial: FinancialSummary,
        prediction: SalesPrediction,
    ) -> list[str]:
        recommendations: list[str] = []

        utilisation = (
            (financial.planned_spend / financial.total_budget * 100)
            if financial.total_budget > 0
            else 0.0
        )

        if utilisation < 50:
            recommendations.append(
                f"Budget utilisation is only {utilisation:.0f}% — consider "
                "accelerating spend on high-impact tasks."
            )
        elif utilisation > 90:
            recommendations.append(
                "Budget is nearly exhausted — prioritise remaining tasks by expected ROI."
            )

        if prediction.method == "unavailable":
            recommendations.append("No sales prediction was made; no sample sales data is used.")
        elif prediction.growth_percent >= 10:
            recommendations.append(
                "Strong growth trend detected — allocate additional marketing "
                "budget to capitalise on momentum."
            )
        elif prediction.growth_percent >= 0:
            recommendations.append(
                "Moderate growth expected — maintain current marketing spend and monitor closely."
            )
        else:
            recommendations.append(
                "Negative growth projected — investigate root causes and "
                "consider targeted promotions."
            )

        return recommendations


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_report_service: ReportService | None = None


def get_report_service() -> ReportService:
    global _report_service
    if _report_service is None:
        _report_service = ReportService(store=get_json_store())
    return _report_service
