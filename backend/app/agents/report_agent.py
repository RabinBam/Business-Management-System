"""Person 2 starting point: narrative interpretation of deterministic report data."""

from __future__ import annotations

from app.schemas.report import Report
from app.schemas.workflow import WorkflowRead
from app.services.report_service import get_report_service


class ReportAgent:
    """Generate and retrieve financial reports for completed workflows.

    The agent coordinates with ``ReportService`` for all arithmetic.  Its
    value-add is assembling the inputs (workflow metadata, task spend) and
    delegating to the service.  When a real AI provider is available it can
    add a narrative summary on top of the deterministic numbers.
    """

    def __init__(self) -> None:
        self._service = get_report_service()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        workflow: WorkflowRead,
        task_spend: float = 0.0,
    ) -> Report:
        """Build a new report for *workflow* and cache it internally.

        Parameters
        ----------
        workflow:
            The workflow being reported on.
        task_spend:
            Total planned/actual spend across workflow tasks.
        """
        return self._service.generate_report(workflow, task_spend=task_spend)

    def get(self, workflow_id: str) -> Report | None:
        """Return a previously generated report, or ``None``."""
        return self._service.get_report(workflow_id)

    def generate_narrative(self, report: Report) -> str:
        """Return a human-readable narrative summary of *report*.

        This is a deterministic placeholder.  When the AI service is
        connected, this method can call the LLM to produce a richer
        executive summary.
        """
        fin = report.financial
        pred = report.sales_prediction

        utilisation = (
            f"{fin.planned_spend / fin.total_budget * 100:.0f}%"
            if fin.total_budget > 0
            else "N/A"
        )

        lines = [
            f"## Financial Summary for Workflow {report.workflow_id}",
            "",
            f"- **Total Budget:** ${fin.total_budget:,.2f}",
            f"- **Planned Spend:** ${fin.planned_spend:,.2f}",
            f"- **Remaining Budget:** ${fin.remaining_budget:,.2f}",
            f"- **Budget Utilisation:** {utilisation}",
            "",
            "## Sales Prediction",
            "",
            f"- **Current Sales:** ${pred.current_sales:,.2f}",
            f"- **Predicted Sales:** ${pred.predicted_sales:,.2f}",
            f"- **Growth:** {pred.growth_percent:+.1f}%",
            f"- **Method:** {pred.method}",
            "",
        ]

        if report.risks:
            lines.append("## Risks")
            lines.append("")
            for risk in report.risks:
                lines.append(f"- {risk}")
            lines.append("")

        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_report_agent: ReportAgent | None = None


def get_report_agent() -> ReportAgent:
    global _report_agent
    if _report_agent is None:
        _report_agent = ReportAgent()
    return _report_agent
