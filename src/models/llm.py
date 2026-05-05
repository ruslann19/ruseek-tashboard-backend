from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class LLMOrm(Base):
    __tablename__ = "llms"

    name: Mapped[str] = mapped_column(unique=True)

    answers: Mapped[list["AnswersOrm"]] = relationship(  # noqa: F821
        back_populates="llm",
        cascade="all, delete-orphan",
    )
