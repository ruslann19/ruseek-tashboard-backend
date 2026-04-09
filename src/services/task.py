from repositories.task import TaskRepository, task_repository
from schemas.task import (
    TaskCreateSchema,
    TaskDeleteSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)


class TaskServise:
    def __init__(self, task_repository: TaskRepository) -> None:
        self.task_repository = task_repository

    def add_task(self, task: TaskCreateSchema) -> TaskReadSchema:
        return self.task_repository.add_task(task)

    def get_all_tasks(self) -> list[TaskReadSchema]:
        return self.task_repository.get_all_tasks()

    def get_task_by_id(self, task_id: int) -> TaskReadSchema:
        return self.task_repository.get_task_by_id(task_id)

    def update_task(self, task_for_update: TaskUpdateSchema) -> TaskReadSchema:
        return self.task_repository.update_task(task_for_update)

    def delete_task(self, task_id: int) -> TaskDeleteSchema:
        return self.task_repository.delete_task(task_id)


task_service = TaskServise(task_repository=task_repository)
