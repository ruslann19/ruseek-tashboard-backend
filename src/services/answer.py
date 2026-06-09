from sqlalchemy.ext.asyncio import AsyncSession

from repositories import AnswerRepository, LlmRepository, TaskRepository
from schemas.answer import AnswerCreateSchema, AnswerReadSchema, AnswerUpdateSchema

from .llm import LlmService
from .task import TaskServise


class AnswerNotFound(Exception):
    """Ответ не найден"""


class AnswerService:
    def __init__(self, repository: AnswerRepository, session: AsyncSession) -> None:
        self.repository = repository
        self.session = session

    async def add_answer(self, answer: AnswerCreateSchema) -> AnswerReadSchema:
        task_repository = TaskRepository(self.session)
        task_service = TaskServise(task_repository, self.session)
        # Если задача не найдётся, то выбростися исключение TaskNotFound
        await task_service.get_task_by_id(answer.task_id)

        llm_repository = LlmRepository(self.session)
        llm_service = LlmService(llm_repository, self.session)
        # Если задача не найдётся, то выбростися исключение LLMNotFound
        await llm_service.get_llm_by_id(answer.llm_id)

        answer_orm = await self.repository.add(**answer.model_dump())
        await self.session.commit()
        return AnswerReadSchema.model_validate(answer_orm)

    async def get_all_answers(self) -> list[AnswerReadSchema]:
        answers_orm = await self.repository.get_all()
        return [
            AnswerReadSchema.model_validate(answer_orm) for answer_orm in answers_orm
        ]

    async def get_answer_by_id(self, answer_id: int) -> AnswerReadSchema:
        answer_orm = await self.repository.get_by_id(answer_id)

        if answer_orm is None:
            raise AnswerNotFound

        return AnswerReadSchema.model_validate(answer_orm)

    async def update_answer(self, answer_data_for_update: AnswerUpdateSchema) -> None:
        answer_id = answer_data_for_update.id

        data = answer_data_for_update.model_dump(exclude_none=True)
        del data["id"]

        if len(data) > 0:
            await self.repository.update(answer_id, **data)
            await self.session.commit()

    async def delete_answer(self, answer_id: int) -> None:
        await self.repository.delete(answer_id)
        await self.session.commit()
