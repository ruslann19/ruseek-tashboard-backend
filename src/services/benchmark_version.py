from sqlalchemy.ext.asyncio import AsyncSession

from models import TaskOrm
from repositories import BenchmarkVersionRepository, TaskRepository
from schemas import BenchmarkVersionCreateSchema, BenchmarkVersionReadSchema


class BenchmarkVersionNotFound(Exception):
    """Версия бенчмарка не найдена"""


class BenchmarkVersionService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.repository = BenchmarkVersionRepository(session)

    async def add(
        self,
        benchmark_version: BenchmarkVersionCreateSchema,
    ) -> BenchmarkVersionReadSchema:
        benchmark_version_orm = await self.repository.add(
            **benchmark_version.model_dump()
        )
        await self.session.commit()
        return BenchmarkVersionReadSchema.model_validate(benchmark_version_orm)

    async def get_all(
        self,
        *expressions,
        **filters,
    ) -> list[BenchmarkVersionReadSchema]:
        benchmark_versions_orm = await self.repository.get_all(*expressions, **filters)
        return [
            BenchmarkVersionReadSchema.model_validate(task_orm)
            for task_orm in benchmark_versions_orm
        ]

    async def get_one_or_none(
        self,
        *expressions,
        **filters,
    ) -> BenchmarkVersionReadSchema | None:
        benchmark_version_orm = await self.repository.get_one_or_none(
            *expressions,
            **filters,
        )
        if benchmark_version_orm is None:
            return None

        return BenchmarkVersionReadSchema.model_validate(benchmark_version_orm)

    async def get_by_id(self, benchmark_version_id: int) -> BenchmarkVersionReadSchema:
        benchmark_version_orm = await self.repository.get_by_id(benchmark_version_id)

        if benchmark_version_orm is None:
            raise BenchmarkVersionNotFound

        return BenchmarkVersionReadSchema.model_validate(benchmark_version_orm)

    async def get_potential_versions(self) -> list[BenchmarkVersionCreateSchema]:
        existing_versions = await self.get_all()
        existing_versions_create_schema = [
            BenchmarkVersionCreateSchema.model_validate(version.model_dump())
            for version in existing_versions
        ]

        task_repository = TaskRepository(self.session)
        not_tested_tasks = await task_repository.get_all(
            TaskOrm.benchmark_version.is_(None),
        )

        potential_versions = set()
        for task in not_tested_tasks:
            version = BenchmarkVersionCreateSchema(
                year=task.published_date.year,
                month=task.published_date.month,
            )

            if version not in existing_versions_create_schema:
                potential_versions.add(version)

        return list(potential_versions)

    async def delete(self, benchmark_version_id: int) -> None:
        await self.repository.delete(benchmark_version_id)
        await self.session.commit()
