from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LlmOrm(Base):
    __tablename__ = "llms"

    llm_name: Mapped[str] = mapped_column(unique=True)

    answers: Mapped[list["AnswerOrm"]] = relationship(  # noqa: F821
        back_populates="llm",
        cascade="all, delete-orphan",
    )
