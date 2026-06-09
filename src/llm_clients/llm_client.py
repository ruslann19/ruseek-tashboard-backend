import asyncio
from abc import ABC, abstractmethod


class LlmClient(ABC):
    @abstractmethod
    async def ask(self, question: str) -> str:
        raise NotImplementedError


class MockLlmClient(LlmClient):
    async def ask(self, question: str) -> str:
        await asyncio.sleep(0.1)
        return "Данный ответ сгенерирован через MockLlmClient"
