from sqlalchemy.orm import Mapped

from .base import Base


class TaskORM(Base):
    __tablename__ = "tasks"

    question: Mapped[str]
    correct_answer: Mapped[str]
    benchmark_version: Mapped[int | None]
    state: Mapped[str]
