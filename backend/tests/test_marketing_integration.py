import asyncio
from datetime import date, timedelta

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
    workflow_id = client.post(
        "/api/v1/workflows",
        json={
            "title": "Marketing test",
            "objective": "Create a measurable marketing campaign.",
            "budget": 25000,
            "deadline": (date.today() + timedelta(days=30)).isoformat(),
        },
    ).json()["data"]["id"]
    assert client.post(f"/api/v1/workflows/{workflow_id}/run").status_code == 200
    payload = {
        "workflow_id": workflow_id,
        "approved_budget": 10_000,
        "objective": "Launch a regional campaign",
        "target_audience": "Local businesses",
        "allocations": [{"channel": "Search", "amount": 6_000, "reason": "Capture demand"}],
        "timeline": ["Week 1: launch"],
        "expected_outcome": "Qualified leads",
    }

    saved = client.put(f"/api/v1/workflows/{workflow_id}/marketing", json=payload)
    loaded = client.get(f"/api/v1/workflows/{workflow_id}/marketing")

    assert saved.status_code == 200
    assert saved.json()["data"] == payload
    assert loaded.status_code == 200
    assert loaded.json()["data"] == payload
    assert (
        client.get(f"/api/v1/workflows/{workflow_id}").json()["data"]["executive_summary"] is None
    )
    assert client.post(f"/api/v1/workflows/{workflow_id}/summary/refresh").json()["data"][
        "executive_summary"
    ]
    payload["approved_budget"] = 999999
    payload["allocations"][0]["amount"] = 999998
    assert client.put(f"/api/v1/workflows/{workflow_id}/marketing", json=payload).status_code == 422
