"""Person 2 starting point for financial arithmetic and report assembly."""

from __future__ import annotations

from app.schemas.report import FinancialSummary, Report, SalesPrediction
from app.schemas.workflow import WorkflowRead
from app.services.prediction_service import get_prediction_service


class ReportService:
    """Assemble deterministic financial data into the shared Report schema.

    All arithmetic lives here, not in the router or the agent. The agent may
    later add a narrative layer on top, but numbers are always computed by
    this service so they remain auditable.
    """

    def __init__(self) -> None:
        self._reports: dict[str, Report] = {}

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

        prediction = self._build_sales_prediction()

        risks = self._assess_risks(financial, prediction)
        recommendations = self._build_recommendations(financial, prediction)

        report = Report(
            workflow_id=workflow.id,
            financial=financial,
            sales_prediction=prediction,
            risks=risks,
            recommendations=recommendations,
        )
        self._reports[workflow.id] = report
        return report

    def get_report(self, workflow_id: str) -> Report | None:
        """Return a previously generated report, or ``None``."""
        return self._reports.get(workflow_id)

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
    def _build_sales_prediction() -> SalesPrediction:
        prediction_service = get_prediction_service()
        return prediction_service.predict_next_quarter()

    @staticmethod
    def _assess_risks(
        financial: FinancialSummary,
        prediction: SalesPrediction,
    ) -> list[str]:
        risks: list[str] = []

        if financial.remaining_budget < 0:
            risks.append(
                "Planned spend exceeds total budget by "
                f"${abs(financial.remaining_budget):,.2f}."
            )
        elif financial.remaining_budget < financial.total_budget * 0.10:
            risks.append(
                "Less than 10% of budget remains — limited room for "
                "unplanned expenses."
            )

        if prediction.growth_percent < 0:
            risks.append(
                f"Sales are projected to decline by "
                f"{abs(prediction.growth_percent):.1f}%."
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
                "Budget is nearly exhausted — prioritise remaining tasks by "
                "expected ROI."
            )

        if prediction.growth_percent >= 10:
            recommendations.append(
                "Strong growth trend detected — allocate additional marketing "
                "budget to capitalise on momentum."
            )
        elif prediction.growth_percent >= 0:
            recommendations.append(
                "Moderate growth expected — maintain current marketing spend "
                "and monitor closely."
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
        _report_service = ReportService()
    return _report_service
