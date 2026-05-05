from sqlalchemy.ext.asyncio import AsyncSession

from repositories.task import TaskRepository
from schemas.task import (
    TaskCreateCoreSchema,
    TaskCreateSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)


class TaskNotFound(Exception):
    """Задача не найдена"""


class TaskServise:
    def __init__(self, repository: TaskRepository, session: AsyncSession) -> None:
        self.repository = repository
        self.session = session

    async def add_task(self, task: TaskCreateCoreSchema) -> TaskReadSchema:
        task_full = TaskCreateSchema.model_validate(task)
        task_orm = await self.repository.create(**task_full.model_dump())
        await self.session.commit()
        return TaskReadSchema.model_validate(task_orm)

    async def get_all_tasks(self) -> list[TaskReadSchema]:
        tasks_orm = await self.repository.get_all()
        return [TaskReadSchema.model_validate(task_orm) for task_orm in tasks_orm]

    async def get_task_by_id(self, task_id: int) -> TaskReadSchema:
        task_orm = await self.repository.get_by_id(task_id)

        if task_orm is None:
            raise TaskNotFound

        return TaskReadSchema.model_validate(task_orm)

    async def update_task(self, task_for_update: TaskUpdateSchema) -> None:
        task_id = task_for_update.id

        data = task_for_update.model_dump(exclude_none=True)
        del data["id"]

        if len(data) > 0:
            await self.repository.update(id=task_id, **data)
            await self.session.commit()

    async def delete_task(self, task_id: int) -> None:
        await self.repository.delete(task_id)
        await self.session.commit()
