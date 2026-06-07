from sqlalchemy.ext.asyncio import AsyncSession

from models import TaskOrm

from .base import BaseRepository


class TaskRepository(BaseRepository[TaskOrm]):
    def __init__(self, session: AsyncSession):
        super().__init__(TaskOrm, session)
