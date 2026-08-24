"""Person 2 starting point for the versioned sales prediction pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from app.schemas.report import SalesPrediction

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class PredictionService:
    """Load quarterly sales data and predict next-quarter revenue.

    Uses a pure-Python ordinary-least-squares linear regression so the
    backend has zero heavy dependencies (no numpy/scipy).
    """

    def __init__(self) -> None:
        data_path = _DATA_DIR / "sales_data.json"
        raw = json.loads(data_path.read_text(encoding="utf-8"))
        self._quarters: list[dict[str, object]] = raw.get("quarters", [])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_sales_data(self) -> list[dict[str, object]]:
        """Return the raw quarter records loaded from disk."""
        return list(self._quarters)

    def predict_next_quarter(self) -> SalesPrediction:
        """Extrapolate the revenue trend and predict the next quarter.

        Returns a ``SalesPrediction`` with ``predicted_sales`` floored at 0.
        """
        if not self._quarters:
            return SalesPrediction(
                current_sales=0.0,
                predicted_sales=0.0,
                growth_percent=0.0,
                method="linear_regression",
            )

        revenues = [float(q.get("revenue", 0.0)) for q in self._quarters]  # type: ignore[arg-type]
        current_sales = revenues[-1]

        slope, intercept = self._linear_regression(revenues)

        # Next x-value is len(revenues) since indices start at 0.
        predicted_sales = max(0.0, slope * len(revenues) + intercept)

        growth_percent = (
            ((predicted_sales - current_sales) / current_sales) * 100
            if current_sales > 0
            else 0.0
        )

        return SalesPrediction(
            current_sales=current_sales,
            predicted_sales=round(predicted_sales, 2),
            growth_percent=round(growth_percent, 2),
            method="linear_regression",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _linear_regression(values: list[float]) -> tuple[float, float]:
        """Pure-Python ordinary-least-squares on *values* indexed 0..n-1.

        Returns ``(slope, intercept)``.

        The formula used is:
            slope     = (n·Σxy − Σx·Σy) / (n·Σx² − (Σx)²)
            intercept = (Σy − slope·Σx) / n
        """
        n = len(values)
        if n == 0:
            return 0.0, 0.0
        if n == 1:
            return 0.0, float(values[0])

        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * y for i, y in enumerate(values))
        sum_xx = sum(i * i for i in range(n))

        denominator = n * sum_xx - sum_x ** 2
        if denominator == 0:
            return 0.0, sum_y / n

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        return slope, intercept


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_prediction_service: PredictionService | None = None


def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service
