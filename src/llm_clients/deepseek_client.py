import asyncio

from openai import AsyncOpenAI

from core.config import settings

from .llm_client import LlmClient


class DeepSeekClient(LlmClient):
    def __init__(
        self,
        model: str = "deepseek-v4-flash",
        temperature: float = 1.0,
        thinking: str = "disabled",
        concurrent_requests: int = 10,
    ) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
        )
        self.model = model
        self.temperature = temperature
        self.thinking = thinking
        self.semaphore = asyncio.Semaphore(concurrent_requests)

    async def ask(self, question: str) -> str:
        async with self.semaphore:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": question},
                ],
                temperature=self.temperature,
                extra_body={"thinking": {"type": self.thinking}},
                stream=False,
            )
            return response.choices[0].message.content
