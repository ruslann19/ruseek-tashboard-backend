from schemas.task import (
    TaskCreateSchema,
    TaskDeleteSchema,
    TaskReadSchema,
    TaskUpdateSchema,
)


class TaskNotFound(Exception):
    """Задача не найдена"""


class TaskRepository:
    def __init__(self) -> None:
        # Временное хранилище (в памяти)
        self.tasks_db: list[TaskReadSchema] = []

    def add_task(self, task: TaskCreateSchema) -> TaskReadSchema:
        task_for_add = TaskReadSchema(
            task_id=len(self.tasks_db) + 1,
            question=task.question,
            correct_answer=task.correct_answer,
            state=task.state,
            source_url=task.source_url,
            benchmark_version=task.benchmark_version,
        )
        self.tasks_db.append(task_for_add)
        return task_for_add

    def get_all_tasks(self) -> list[TaskReadSchema]:
        return self.tasks_db

    def get_task_by_id(self, task_id: int) -> TaskReadSchema:
        for task in self.tasks_db:
            if task.task_id == task_id:
                return task

        raise TaskNotFound()

    def update_task(self, task_for_update: TaskUpdateSchema) -> TaskReadSchema:
        for task in self.tasks_db:
            if task.task_id == task_for_update.task_id:
                if task_for_update.question is not None:
                    task.question = task_for_update.question

                if task_for_update.correct_answer is not None:
                    task.correct_answer = task_for_update.correct_answer

                if task_for_update.state is not None:
                    task.state = task_for_update.state

                if task_for_update.source_url is not None:
                    task.source_url = task_for_update.source_url

                if task_for_update.benchmark_version is not None:
                    task.benchmark_version = task_for_update.benchmark_version

                return task

        raise TaskNotFound()

    def delete_task(self, task_id: int) -> TaskDeleteSchema:
        for task in self.tasks_db:
            if task.task_id == task_id:
                self.tasks_db.remove(task)
                return TaskDeleteSchema(deleted=True)

        raise TaskNotFound()


task_repository = TaskRepository()
