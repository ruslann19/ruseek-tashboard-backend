from datetime import date

from sqlalchemy.orm import Mapped, relationship

from .base import Base


class TaskOrm(Base):
    __tablename__ = "tasks"

    question: Mapped[str]
    correct_answer: Mapped[str]
    benchmark_version: Mapped[int | None]
    state: Mapped[str]

    published_date: Mapped[date]
    source_url: Mapped[str]

    answers: Mapped[list["AnswerOrm"]] = relationship(  # noqa: F821
        back_populates="task",
        cascade="all, delete-orphan",
    )
