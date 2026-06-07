from typing import Generic, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Определяем тип для моделей
T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def add(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()  # Получаем ID без коммита
        return instance

    async def add_all(self, items_data: list[dict]) -> list[T]:
        instances = [self.model(**data) for data in items_data]
        self.session.add_all(instances)
        await self.session.flush()  # Получаем ID для всех объектов без коммита
        return instances

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self, **filters) -> list[T]:
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_one_or_none(self, **filters) -> T | None:
        query = select(self.model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_complex_filter(self, *expressions) -> list[T]:
        """
        Принимает конструкции вида: Model.age > 18, Model.name.like("%Иван%")
        """
        query = select(self.model).where(*expressions)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, id: int, **kwargs):
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(query)

    async def delete(self, id: int):
        query = delete(self.model).where(self.model.id == id)
        await self.session.execute(query)
