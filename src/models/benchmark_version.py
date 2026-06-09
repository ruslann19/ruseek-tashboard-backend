from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from .base import Base


class BenchmarkVersionOrm(Base):
    __tablename__ = "benchmark_versions"

    year: Mapped[int]
    month: Mapped[int]

    answers: Mapped[list["AnswerOrm"]] = relationship(  # noqa: F821
        back_populates="benchmark_version",
        cascade="all, delete-orphan",
    )

    __table_args__ = (UniqueConstraint("year", "month", name="unique_year_and_month"),)
