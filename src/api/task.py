from fastapi import APIRouter, HTTPException

from repositories.task import TaskNotFound
from schemas.task import (
    TaskCreateSchema,
    TaskDeleteSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)
from services.task import task_service

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


# Создать новую задачу
@router.post("/", response_model=TaskReadSchema)
async def create_task(task: TaskCreateSchema):
    return task_service.add_task(task)


# Получить все задачи
@router.get("/", response_model=list[TaskReadSchema])
async def get_tasks():
    return task_service.get_all_tasks()


# Получить конкретную задачу по ID
@router.get("/{task_id}", response_model=TaskReadSchema)
async def get_task(task_id: int):
    try:
        task = task_service.get_task_by_id(task_id)
        return task
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Задача не найдена")


@router.put("/{task_id}", response_model=TaskReadSchema)
async def update_task(task_for_update: TaskUpdateSchema):
    try:
        updated_task = task_service.update_task(task_for_update)
        return updated_task
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Задача не найдена")


@router.delete("/{task_id}", response_model=TaskDeleteSchema)
async def delete_task(task_id: int):
    try:
        delete_response = task_service.delete_task(task_id)
        return delete_response
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Задача не найдена")
