from pydantic import BaseModel, ConfigDict, Field


class AnswerCreateSchema(BaseModel):
    task_id: int
    llm_id: int
    benchmark_version_id: int
    llm_answer: str
    is_correct: bool | None = Field(default=None, examples=[None])
    judge_explaination: str | None = Field(default=None, examples=[None])

    model_config = ConfigDict(from_attributes=True)


class AnswerReadSchema(AnswerCreateSchema):
    id: int


class AnswerUpdateSchema(BaseModel):
    id: int
    llm_answer: str | None = Field(default=None, examples=[None])
    is_correct: bool | None = Field(default=None, examples=[None])
    judge_explaination: str | None = Field(default=None, examples=[None])
