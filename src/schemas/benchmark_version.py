from typing import Literal

from pydantic import BaseModel, ConfigDict


class BenchmarkVersionCreateSchema(BaseModel):
    year: int
    month: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    model_config = ConfigDict(from_attributes=True, frozen=True)

    def __lt__(self, other):
        if not isinstance(other, BenchmarkVersionCreateSchema):
            return NotImplemented
        # Сравниваем сначала по году, а при равенстве — по месяцу
        return (self.year, self.month) < (other.year, other.month)

    def __eq__(self, other):
        if not isinstance(other, BenchmarkVersionCreateSchema):
            return NotImplemented
        return (self.year, self.month) == (other.year, other.month)


class BenchmarkVersionReadSchema(BenchmarkVersionCreateSchema):
    id: int
