from sqlalchemy.orm import Mapped, relationship

from .base import Base


class TaskORM(Base):
    __tablename__ = "tasks"

    question: Mapped[str]
    correct_answer: Mapped[str]
    benchmark_version: Mapped[int | None]
    state: Mapped[str]

    answers: Mapped[list["AnswerORM"]] = relationship(  # noqa: F821
        back_populates="task",
        cascade="all, delete-orphan",
    )
