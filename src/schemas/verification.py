from typing import Literal

from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    question: str
    correct_answer: str
    llm_answer: str


class VerificationResponse(BaseModel):
    explaination: str = Field(..., description="Почему принято такое решение")
    verdict: Literal["RIGHT", "WRONG", "FORMAT_ERROR"]
