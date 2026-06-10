from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AnswerOrm(Base):
    __tablename__ = "answers"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    llm_id: Mapped[int] = mapped_column(ForeignKey("llms.id", ondelete="CASCADE"))
    benchmark_version_id: Mapped[int] = mapped_column(
        ForeignKey("benchmark_versions.id", ondelete="CASCADE")
    )
    llm_answer: Mapped[str]
    is_correct: Mapped[bool | None]
    judge_explaination: Mapped[str | None]

    task: Mapped[list["TaskOrm"]] = relationship(back_populates="answers")  # noqa: F821
    llm: Mapped[list["LlmOrm"]] = relationship(back_populates="answers")  # noqa: F821
    benchmark_version: Mapped[list["BenchmarkVersionOrm"]] = relationship(  # noqa: F821
        back_populates="answers"
    )

    __table_args__ = (
        UniqueConstraint("id", "task_id", "llm_id", name="uq_answer_id_task_llm"),
    )
