from pydantic import BaseModel

ON_VALIDATION_STATE = "on validation"
QUEUE_STATE = "queue"
BENCHMARK_STATE = "benchmark"
ARCHIVE_STATE = "archive"


class TaskCreateSchema(BaseModel):
    question: str
    correct_answer: str
    state: str = QUEUE_STATE
    source_url: str | None = None
    benchmark_version: int | None = None


class TaskReadSchema(TaskCreateSchema):
    task_id: int


class TaskUpdateSchema(BaseModel):
    # обязательный параметр
    task_id: int
    # необязательные параметры
    question: str | None = None
    correct_answer: str | None = None
    state: str | None = None
    source_url: str | None = None
    benchmark_version: int | None = None


class TaskDeleteSchema(BaseModel):
    deleted: bool
