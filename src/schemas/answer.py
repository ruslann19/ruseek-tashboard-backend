from pydantic import BaseModel, Field


class AnswerCreateSchema(BaseModel):
    task_id: int
    llm_id: int
    answer: str
    is_correct: bool | None = Field(default=None, examples=[None])


class AnswerReadSchema(AnswerCreateSchema):
    id: int
