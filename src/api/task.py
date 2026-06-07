from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories import TaskRepository
from schemas import (
    BenchmarkVersion,
    TaskCreateCoreSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)
from services import TaskServise
from services.task import TaskNotFound

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


async def get_task_repository(session: AsyncSession = Depends(get_async_session)):
    return TaskRepository(session)


async def get_task_service(repository: TaskRepository = Depends(get_task_repository)):
    return TaskServise(repository, repository.session)


@router.post(
    "/",
    response_model=TaskReadSchema,
    summary="Создать новую задачу",
)
async def create_task(
    task: TaskCreateCoreSchema,
    task_service: TaskServise = Depends(get_task_service),
):
    return await task_service.add_task(task)


@router.get(
    "/",
    response_model=list[TaskReadSchema],
    summary="Получить все задачи",
)
async def get_tasks(
    task_service: TaskServise = Depends(get_task_service),
):
    return await task_service.get_all_tasks()


@router.get(
    "/benchmark-versions",
    response_model=dict[str, list[BenchmarkVersion]],
    summary="Получить список версий бенчмарка (имеющихся и потенциальных)",
)
async def get_benchmark_versions(
    task_service: TaskServise = Depends(get_task_service),
):
    return await task_service.get_benchmark_versions()


@router.get(
    "/{task_id}",
    response_model=TaskReadSchema,
    summary="Получить конкретную задачу по ID",
)
async def get_task(
    task_id: int,
    task_service: TaskServise = Depends(get_task_service),
):
    try:
        return await task_service.get_task_by_id(task_id)
    except TaskNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена",
        )


@router.put(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить конкретную задачу по ID",
)
async def update_task(
    task_for_update: TaskUpdateSchema,
    task_service: TaskServise = Depends(get_task_service),
):
    await task_service.update_task(task_for_update)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить конкретную задачу по ID",
)
async def delete_task(
    task_id: int,
    task_service: TaskServise = Depends(get_task_service),
):
    await task_service.delete_task(task_id)
