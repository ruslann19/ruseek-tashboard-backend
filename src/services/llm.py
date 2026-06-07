from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import LlmRepository
from schemas.llm import LlmCreateSchema, LlmReadSchema, LlmUpdateSchema


class LlmNotFound(Exception):
    """LLM не найдена"""


class LlmAlreadyExists(Exception):
    """LLM уже существует"""


class LlmService:
    def __init__(self, repository: LlmRepository, session: AsyncSession) -> None:
        self.repository = repository
        self.session = session

    async def add_llm(self, llm: LlmCreateSchema) -> LlmReadSchema:
        try:
            llm_orm = await self.repository.add(**llm.model_dump())
            await self.session.commit()
            return LlmReadSchema.model_validate(llm_orm)
        except IntegrityError:
            raise LlmAlreadyExists

    async def get_all_llms(self) -> list[LlmReadSchema]:
        llms_orm = await self.repository.get_all()
        return [LlmReadSchema.model_validate(llm_orm) for llm_orm in llms_orm]

    async def get_llm_by_id(self, task_id: int) -> LlmReadSchema:
        llm_orm = await self.repository.get_by_id(task_id)

        if llm_orm is None:
            raise LlmNotFound

        return LlmReadSchema.model_validate(llm_orm)

    async def update_llm(self, llm_data_for_update: LlmUpdateSchema) -> None:
        llm_id = llm_data_for_update.id

        data = llm_data_for_update.model_dump(exclude_none=True)
        del data["id"]

        if len(data) > 0:
            await self.repository.update(llm_id, **data)
            await self.session.commit()

    async def delete_llm(self, llm_id: int) -> None:
        await self.repository.delete(llm_id)
        await self.session.commit()
