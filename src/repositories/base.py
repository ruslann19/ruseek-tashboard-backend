from typing import Generic, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

# Определяем тип для моделей
T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        return instance

    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def get_all(self) -> list[T]:
        query = select(self.model)
        return list(self.session.execute(query).scalars().all())

    def update(self, id: int, **kwargs):
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        self.session.execute(query)

    def delete(self, id: int):
        query = delete(self.model).where(self.model.id == id)
        self.session.execute(query)
