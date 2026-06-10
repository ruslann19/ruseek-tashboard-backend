import asyncio

from openai import AsyncOpenAI

from core.config import running_modes, settings

from .llm_client import LlmClient, MockLlmClient


class RouterAiClient(LlmClient):
    def __init__(
        self,
        model: str,
        temperature: float = 1.0,
        concurrent_requests: int = 10,
        reasoning_effort="none",
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.ROUTERAI_API_KEY,
            base_url="https://routerai.ru/api/v1",
        )
        self.model = model
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort
        self.semaphore = asyncio.Semaphore(concurrent_requests)

    async def ask(self, question: str) -> str:
        async with self.semaphore:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
                extra_body={
                    "provider": {
                        "allow_fallbacks": False,
                    },
                },
                reasoning_effort=self.reasoning_effort,
                temperature=self.temperature,
                stream=False,
            )
            return response.choices[0].message.content


def get_router_ai_client(model: str) -> LlmClient:
    if settings.RUNNING_MODE == running_modes.dev:
        return MockLlmClient()
    elif settings.RUNNING_MODE == running_modes.prod:
        return RouterAiClient(model=model)
