"""
Prediction service module.
"""
import json
from pathlib import Path
from app.schemas.report import SalesPrediction

class PredictionService:
    def __init__(self):
        # Path to data directory: backend/data/
        # __file__ is backend/app/services/prediction_service.py
        data_path = Path(__file__).resolve().parent.parent.parent / "data" / "sales_data.json"
        with data_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.quarters = data.get("quarters", [])

    def get_sales_data(self) -> list[dict]:
        return self.quarters

    def _linear_regression(self, values: list[float]) -> tuple[float, float]:
        """
        Pure-Python implementation of simple linear regression (least squares).
        Calculates the slope and intercept for a given list of y-values.
        x-values are assumed to be indices 0, 1, 2, ..., n-1.
        """
        n = len(values)
        if n == 0:
            return 0.0, 0.0
        if n == 1:
            return 0.0, float(values[0])
            
        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in enumerate(values))
        sum_xx = sum(x * x for x in range(n))

        # slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x ** 2)
        denominator = (n * sum_xx - sum_x ** 2)
        if denominator == 0:
            return 0.0, sum_y / n
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        # intercept = (sum_y - slope * sum_x) / n
        intercept = (sum_y - slope * sum_x) / n

        return slope, intercept

    def predict_next_quarter(self) -> SalesPrediction:
        if not self.quarters:
            return SalesPrediction(
                current_sales=0.0,
                predicted_sales=0.0,
                growth_percent=0.0,
                method="linear_regression"
            )
            
        revenues = [float(q.get("revenue", 0.0)) for q in self.quarters]
        current_sales = revenues[-1]
        
        slope, intercept = self._linear_regression(revenues)
        
        # Next x-value is the length of the list, since indices start at 0
        predicted_sales = max(0.0, slope * len(revenues) + intercept)
        
        if current_sales > 0:
            growth_percent = ((predicted_sales - current_sales) / current_sales) * 100
        else:
            growth_percent = 0.0
            
        return SalesPrediction(
            current_sales=current_sales,
            predicted_sales=predicted_sales,
            growth_percent=growth_percent,
            method="linear_regression"
        )


_prediction_service: PredictionService | None = None

def get_prediction_service() -> PredictionService:
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service
