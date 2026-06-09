import calendar
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from models import TaskOrm
from repositories.benchmark_version import BenchmarkVersionRepository
from repositories.task import TaskRepository
from schemas import (
    BenchmarkVersionCreateSchema,
    TaskCreateCoreSchema,
    TaskCreateSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)


class TaskNotFound(Exception):
    """Задача не найдена"""


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = TaskRepository(session)

    async def add_task(self, task: TaskCreateCoreSchema) -> TaskReadSchema:
        task_full = TaskCreateSchema.model_validate(task)
        task_orm = await self.repository.add(**task_full.model_dump())
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

    async def get_benchmark_versions(
        self,
    ) -> dict[str, list[BenchmarkVersionCreateSchema]]:
        # Существующие версии бенчмарка
        versions_repository = BenchmarkVersionRepository(self.session)
        existing_versions_orm = await versions_repository.get_all()
        existing_versions = [
            BenchmarkVersionCreateSchema.model_validate(version)
            for version in existing_versions_orm
        ]

        # Потенциальные версии бенчмарка
        not_tested_tasks = await self.repository.get_all(
            TaskOrm.benchmark_version.is_(None)
        )
        potential_versions = set()
        for task in not_tested_tasks:
            version = BenchmarkVersionCreateSchema(
                year=task.published_date.year,
                month=task.published_date.month,
            )

            if version not in existing_versions:
                potential_versions.add(version)

        return {
            "existing": sorted(existing_versions),
            "potential": sorted(list(potential_versions)),
        }

    async def get_tasks_by_month(self, year: int, month: int) -> list[TaskReadSchema]:
        start_date = date(year, month, 1)

        _, last_day = calendar.monthrange(year, month)
        end_date = date(year, month, last_day)

        tasks_orm = await self.repository.get_all(
            TaskOrm.published_date.between(start_date, end_date)
        )
        tasks = [TaskReadSchema.model_validate(task) for task in tasks_orm]
        return tasks
