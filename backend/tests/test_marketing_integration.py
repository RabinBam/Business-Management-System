import asyncio

from fastapi.testclient import TestClient

from app.agents.marketing_agent import MarketingAgent
from app.main import app
from app.services.ai_service import MockAIProvider
from app.services.marketing_service import MarketingService, marketing_service


def test_marketing_agent_uses_the_shared_structured_ai_contract() -> None:
    service = MarketingService(MarketingAgent(MockAIProvider()))

    plan = asyncio.run(
        service.generate_plan(
            workflow_id="wf-test",
            product_brief="Grow regional product awareness",
            max_budget=100_000,
            approved_context={"growth_percent": 12.5},
        )
    )

    assert plan.workflow_id == "wf-test"
    assert plan.approved_budget == 100_000
    assert sum(item.amount for item in plan.allocations) <= plan.approved_budget


def test_saved_marketing_plan_can_be_loaded_through_the_api() -> None:
    marketing_service.clear()
    client = TestClient(app)
    payload = {
        "workflow_id": "wf-test",
        "approved_budget": 10_000,
        "objective": "Launch a regional campaign",
        "target_audience": "Local businesses",
        "allocations": [
            {"channel": "Search", "amount": 6_000, "reason": "Capture demand"}
        ],
        "timeline": ["Week 1: launch"],
        "expected_outcome": "Qualified leads",
    }

    saved = client.put("/api/v1/workflows/wf-test/marketing", json=payload)
    loaded = client.get("/api/v1/workflows/wf-test/marketing")

    assert saved.status_code == 200
    assert saved.json()["data"] == payload
    assert loaded.status_code == 200
    assert loaded.json()["data"] == payload
