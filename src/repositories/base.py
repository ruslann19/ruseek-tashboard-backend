from typing import Generic, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Определяем тип для моделей
T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()  # Получаем ID без коммита
        return instance

    async def get_by_id(self, id: int) -> T | None:
        return await self.session.get(self.model, id)

    async def get_all(self) -> list[T]:
        query = select(self.model)
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
