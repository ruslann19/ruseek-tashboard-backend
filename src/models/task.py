from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str]
    correct_answer: Mapped[str]
    benchmark_version: Mapped[int | None]
    state: Mapped[str]
