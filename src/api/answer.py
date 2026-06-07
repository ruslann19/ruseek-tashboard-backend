from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories import AnswerRepository
from schemas.answer import AnswerCreateSchema, AnswerReadSchema, AnswerUpdateSchema
from services import AnswerService
from services.answer import AnswerNotFound
from services.llm import LlmNotFound
from services.task import TaskNotFound


async def get_answer_repository(session: AsyncSession = Depends(get_async_session)):
    return AnswerRepository(session)


async def get_answer_service(
    repository: AnswerRepository = Depends(get_answer_repository),
):
    return AnswerService(repository, repository.session)


router = APIRouter(
    prefix="/answers",
    tags=["Ответы"],
)


@router.post(
    "/",
    response_model=AnswerReadSchema,
    summary="Создать новый ответ",
)
async def create_answer(
    answer: AnswerCreateSchema,
    answer_service: AnswerService = Depends(get_answer_service),
):
    try:
        return await answer_service.create_answer(answer)
    except TaskNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Соответствующая задача не найдена",
        )
    except LlmNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Соответствующая LLM не найдена",
        )


@router.get(
    "/",
    response_model=list[AnswerReadSchema],
    summary="Получить все ответы",
)
async def get_answers(
    answer_service: AnswerService = Depends(get_answer_service),
):
    return await answer_service.get_all_answers()


@router.get(
    "/{answer_id}",
    response_model=AnswerReadSchema,
    summary="Получить конкретный ответ по ID",
)
async def get_answer_by_id(
    answer_id: int,
    answer_service: AnswerService = Depends(get_answer_service),
):
    try:
        return await answer_service.get_answer_by_id(answer_id)
    except AnswerNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ответ не найден",
        )


@router.put(
    "/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить конкретный ответ по ID",
)
async def update_answer(
    answer_data_for_update: AnswerUpdateSchema,
    answer_service: AnswerService = Depends(get_answer_service),
):
    await answer_service.update_answer(answer_data_for_update)


@router.delete(
    "/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить конкретный ответ по ID",
)
async def delete_answer(
    answer_id: int,
    answer_service: AnswerService = Depends(get_answer_service),
):
    await answer_service.delete_answer(answer_id)
