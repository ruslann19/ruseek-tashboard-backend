import asyncio
from abc import ABC, abstractmethod

import instructor
from instructor.core.exceptions import InstructorRetryException
from openai import AsyncOpenAI

from core.config import running_modes, settings
from schemas.verification import (
    VerificationRequest,
    VerificationResponse,
)


class Judge(ABC):
    @abstractmethod
    async def verify(self, request: VerificationRequest) -> VerificationResponse:
        raise NotImplementedError


class MockJudge(Judge):
    async def verify(self, request: VerificationRequest) -> VerificationResponse:
        await asyncio.sleep(0.1)
        return VerificationResponse(
            explaination="Данный ответ сгенерирован через MockJudge",
            verdict="FORMAT_ERROR",
        )


class LlmJudge(Judge):
    def __init__(
        self,
        prompt_template_path: str = "./prompt_templates/llm_as_a_judge.txt",
        api_key: str = settings.DEEPSEEK_API_KEY,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-v4-flash",
        concurrent_requests: int = 10,
    ) -> None:
        self.prompt_template_path = prompt_template_path
        with open(self.prompt_template_path) as f:
            self.prompt_template = f.read()

        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        self.llm_client = instructor.from_openai(
            AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            ),
            mode=instructor.Mode.JSON,
        )
        self.semaphore = asyncio.Semaphore(concurrent_requests)

    async def verify(self, request: VerificationRequest) -> VerificationResponse:
        prompt = self.prompt_template.format(
            question=request.question,
            correct_answer=request.correct_answer,
            llm_answer=request.llm_answer,
        )

        async with self.semaphore:
            try:
                response = await self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0,
                    response_model=VerificationResponse,
                    max_retries=3,  # Автоматические повторные попытки
                )

                return response

            except InstructorRetryException:
                return VerificationResponse(
                    explaination="Не удалось получить ответ от LLM-as-a-judge в нужном формате",
                    verdict="FORMAT_ERROR",
                )


def get_judge() -> Judge:
    if settings.RUNNING_MODE == running_modes.dev:
        return MockJudge()
    elif settings.RUNNING_MODE == running_modes.prod:
        return LlmJudge()
