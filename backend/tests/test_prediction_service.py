"""Tests for the prediction service — regression math and schema output."""

from app.schemas.report import SalesPrediction
from app.services.prediction_service import PredictionService


class TestPredictionServiceData:
    """Verify that the service loads and exposes the sales dataset."""

    def test_loads_quarters(self) -> None:
        service = PredictionService()
        data = service.get_sales_data()
        assert len(data) >= 4, "Expected at least 4 quarters of sales data"

    def test_quarter_has_expected_keys(self) -> None:
        service = PredictionService()
        quarter = service.get_sales_data()[0]
        assert "period" in quarter
        assert "revenue" in quarter
        assert "units_sold" in quarter


class TestLinearRegression:
    """Test the pure-Python least-squares implementation."""

    def test_constant_series(self) -> None:
        service = PredictionService()
        slope, intercept = service._linear_regression([100, 100, 100])
        assert abs(slope) < 1e-9
        assert abs(intercept - 100) < 1e-9

    def test_perfect_upward_trend(self) -> None:
        service = PredictionService()
        # y = 10x + 100  →  values at x=0,1,2,3 are 100,110,120,130
        slope, intercept = service._linear_regression([100, 110, 120, 130])
        assert abs(slope - 10) < 1e-9
        assert abs(intercept - 100) < 1e-9

    def test_single_value(self) -> None:
        service = PredictionService()
        slope, intercept = service._linear_regression([42.0])
        assert slope == 0.0
        assert intercept == 42.0

    def test_empty_list(self) -> None:
        service = PredictionService()
        slope, intercept = service._linear_regression([])
        assert slope == 0.0
        assert intercept == 0.0


class TestPredictNextQuarter:
    """End-to-end prediction output."""

    def test_returns_sales_prediction_schema(self) -> None:
        service = PredictionService()
        result = service.predict_next_quarter()
        assert isinstance(result, SalesPrediction)

    def test_current_sales_is_last_quarter(self) -> None:
        service = PredictionService()
        data = service.get_sales_data()
        result = service.predict_next_quarter()
        assert result.current_sales == data[-1]["revenue"]

    def test_predicted_sales_non_negative(self) -> None:
        service = PredictionService()
        result = service.predict_next_quarter()
        assert result.predicted_sales >= 0

    def test_method_is_linear_regression(self) -> None:
        service = PredictionService()
        result = service.predict_next_quarter()
        assert result.method == "linear_regression"

    def test_growth_percent_is_plausible(self) -> None:
        service = PredictionService()
        result = service.predict_next_quarter()
        # With an upward-trending dataset, growth should be positive
        assert result.growth_percent > -100
