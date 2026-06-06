from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories import TaskRepository
from schemas.task import (
    TaskCreateCoreSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)
from schemas.your_own_game import YourOwnGameMetadata
from services import TaskServise
from services.task import TaskNotFound
from utils.parse_tasks import parse_tasks

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


@router.websocket(
    "/parse-game",
    # summary='Добавить задачи из выпуска передачи "Своя игра"',
    # response_model=list[TaskReadSchema],
)
async def collect_tasks(
    game_metadata: YourOwnGameMetadata,
    task_service: TaskServise = Depends(get_task_service),
):
    with open("./temporary_files/game_example.txt", "r") as f:
        text = f.read()

    added_tasks = []

    print(f"Game metadata: {game_metadata}")

    # async for task in parse_tasks(text, game_metadata):
    #     # print("Поймали задачу асинхронно!")
    #     # print(f"Вопрос: {task.question}")
    #     # print(f"Ответ: {task.correct_answer}")
    #     # print("-" * 20)

    #     added_task = await task_service.add_task(task)
    #     added_tasks.append(added_task)

    return added_tasks


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
