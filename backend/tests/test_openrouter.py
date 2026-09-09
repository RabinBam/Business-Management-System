import asyncio
import json

import httpx
import pytest
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import Settings
from app.services.ai_service import (
    AIConfigurationError,
    AIResponseError,
    AIServiceError,
    OpenRouterProvider,
)


class Output(BaseModel):
    value: str


def completion(content: str) -> dict:
    return {
        "id": "test",
        "object": "chat.completion",
        "created": 1,
        "model": "test/model",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": content},
            }
        ],
    }


def run_response(payload: dict, *, status: int = 200):
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(status, json=payload)

    async def run():
        async with AsyncOpenAI(
            api_key="test-secret",
            base_url="https://openrouter.ai/api/v1",
            max_retries=0,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(handle)),
        ) as client:
            provider = OpenRouterProvider(Settings(ai_primary_model="test/model"), client=client)
            result = await provider.generate_structured(
                system_prompt="system",
                user_prompt="user",
                schema=Output,
                model="test/worker",
            )
            return result, calls

    return asyncio.run(run())


def test_openrouter_real_sdk_request_and_validation():
    result, calls = run_response(completion('{"value":"ready"}'))
    assert result.value == "ready"
    assert str(calls[0].url) == "https://openrouter.ai/api/v1/chat/completions"
    assert calls[0].headers["authorization"] == "Bearer test-secret"
    body = json.loads(calls[0].content)
    assert body["model"] == "test/worker"
    assert body["response_format"]["type"] == "json_schema"
    assert body["response_format"]["json_schema"]["strict"] is True
    assert body["provider"]["require_parameters"] is True


@pytest.mark.parametrize("content", ['{"value": 123}', "not json"])
def test_openrouter_rejects_invalid_output(content):
    with pytest.raises(AIResponseError):
        run_response(completion(content))


def test_openrouter_rejects_empty_choices():
    payload = completion("{}")
    payload["choices"] = []
    with pytest.raises(AIResponseError):
        run_response(payload)


def test_openrouter_sanitizes_provider_error():
    with pytest.raises(AIServiceError) as error:
        run_response({"error": {"message": "test-secret", "code": 401}}, status=401)
    assert "test-secret" not in str(error.value)
    assert "AuthenticationError" in str(error.value)


def test_openrouter_requires_key_and_model():
    with pytest.raises(AIConfigurationError, match="OPENROUTER_API_KEY"):
        OpenRouterProvider(Settings(ai_primary_model="test/model", openrouter_api_key=""))
    with pytest.raises(AIConfigurationError, match="AI_PRIMARY_MODEL"):
        OpenRouterProvider(Settings(ai_primary_model="", openrouter_api_key="secret"))
    assert "secret" not in repr(Settings(openrouter_api_key="secret", openai_api_key="secret"))


@pytest.mark.parametrize(
    "status, guidance",
    [
        (400, "structured-output"),
        (401, "invalid or expired"),
        (402, "Insufficient OpenRouter credits"),
        (403, "Access was denied"),
        (404, "model endpoint"),
        (429, "rate limit"),
        (503, "availability"),
    ],
)
def test_openrouter_status_errors_are_actionable_without_exposing_body(status, guidance):
    with pytest.raises(AIServiceError) as error:
        run_response({"error": {"message": "test-secret", "code": status}}, status=status)
    message = str(error.value)
    assert f"HTTP {status}" in message
    assert guidance in message
    assert "test-secret" not in message


def test_provider_factory_selects_openrouter(monkeypatch):
    from app.services import ai_service

    monkeypatch.setattr(
        ai_service,
        "settings",
        Settings(
            ai_provider="openrouter",
            ai_primary_model="test/model",
            openrouter_api_key="secret",
        ),
    )
    ai_service.get_ai_service.cache_clear()
    try:
        provider = ai_service.get_ai_service()
        assert isinstance(provider, OpenRouterProvider)
        asyncio.run(provider._client.close())
    finally:
        ai_service.get_ai_service.cache_clear()


def test_openrouter_null_choices_is_actionable():
    payload = completion("{}")
    payload["choices"] = None
    with pytest.raises(AIResponseError, match="incomplete response"):
        run_response(payload)
