from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.config import Settings
from app.services.ai_service import (
    AIConfigurationError,
    MockAIProvider,
    OpenAIProvider,
)


class ExampleOutput(BaseModel):
    value: str


class FakeResponses:
    def __init__(self, parsed: object) -> None:
        self.parsed = parsed
        self.calls: list[dict[str, object]] = []

    async def parse(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(output_parsed=self.parsed)


class FakeOpenAIClient:
    def __init__(self, parsed: object) -> None:
        self.responses = FakeResponses(parsed)


def test_mock_provider_returns_queued_structured_response() -> None:
    provider = MockAIProvider({ExampleOutput: [{"value": "ready"}]})
    result = __import__("asyncio").run(
        provider.generate_structured(
            system_prompt="system",
            user_prompt="user",
            schema=ExampleOutput,
        )
    )
    assert result == ExampleOutput(value="ready")


def test_openai_provider_uses_responses_parse_without_storage() -> None:
    client = FakeOpenAIClient({"value": "parsed"})
    provider = OpenAIProvider(
        Settings(ai_primary_model="test-model"),
        client=client,  # type: ignore[arg-type]
    )
    result = __import__("asyncio").run(
        provider.generate_structured(
            system_prompt="follow the schema",
            user_prompt="return a value",
            schema=ExampleOutput,
        )
    )

    assert result.value == "parsed"
    assert client.responses.calls[0]["model"] == "test-model"
    assert client.responses.calls[0]["text_format"] is ExampleOutput
    assert client.responses.calls[0]["store"] is False


def test_openai_provider_requires_credentials_and_model() -> None:
    with pytest.raises(AIConfigurationError, match="OPENAI_API_KEY"):
        OpenAIProvider(Settings(ai_provider="openai", ai_primary_model="test-model"))

    with pytest.raises(AIConfigurationError, match="AI_PRIMARY_MODEL"):
        OpenAIProvider(
            Settings(ai_provider="openai", openai_api_key="secret"),
        )
