from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AnswerORM(Base):
    __tablename__ = "answers"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    llm_id: Mapped[int] = mapped_column(ForeignKey("llms.id", ondelete="CASCADE"))
    answer: Mapped[str]
    is_correct: Mapped[bool | None]

    task: Mapped[list["TaskORM"]] = relationship(back_populates="answers")  # noqa: F821
    llm: Mapped[list["LLMORM"]] = relationship(back_populates="answers")  # noqa: F821
