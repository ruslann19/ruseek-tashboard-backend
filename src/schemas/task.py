from datetime import date

from pydantic import BaseModel, ConfigDict, Field

ON_VALIDATION_STATE = "on validation"
QUEUE_STATE = "queue"
BENCHMARK_STATE = "benchmark"
ARCHIVE_STATE = "archive"


class TaskCreateCoreSchema(BaseModel):
    question: str
    correct_answer: str
    published_date: date
    source_url: str

    model_config = ConfigDict(from_attributes=True)


class TaskCreateSchema(TaskCreateCoreSchema):
    state: str = QUEUE_STATE
    benchmark_version: int | None = Field(default=None, examples=[None])


class TaskReadSchema(TaskCreateSchema):
    id: int


class TaskUpdateSchema(BaseModel):
    # обязательный параметр
    id: int

    # необязательные параметры
    question: str | None = Field(default=None, examples=[None])
    correct_answer: str | None = Field(default=None, examples=[None])
    state: str | None = Field(default=None, examples=[None])
    benchmark_version: int | None = Field(default=None, examples=[None])
    published_date: date | None = Field(default=None, examples=[None])
    source_url: str | None = Field(default=None, examples=[None])
