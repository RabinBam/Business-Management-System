from typing import Protocol, TypeVar

from pydantic import BaseModel

SchemaT = TypeVar("SchemaT", bound=BaseModel)


class AIService(Protocol):
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaT],
        model: str | None = None,
    ) -> SchemaT: ...


class MockAIProvider:
    """Credential-free provider for integration work and deterministic tests."""

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: type[SchemaT],
        model: str | None = None,
    ) -> SchemaT:
        del system_prompt, user_prompt, model
        raise NotImplementedError(
            f"Add a fixture for {schema.__name__} or configure a real AI provider."
        )


def get_ai_service() -> AIService:
    # Person 1: select a provider from settings and keep that choice in this module.
    return MockAIProvider()

