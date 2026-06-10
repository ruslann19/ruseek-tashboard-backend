from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas import AnswerReadSchema
from services import AnswerService
from services.answer import AnswerNotFound


async def get_answer_service(session: AsyncSession = Depends(get_async_session)):
    return AnswerService(session)


router = APIRouter(
    prefix="/answers",
    tags=["Ответы"],
)


@router.get(
    "",
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


@router.get(
    path="/by-benchmark-version/{benchmark_version_id}",
    response_model=list[AnswerReadSchema],
    summary="Получить все ответы в конкретной версии бенчмарка",
)
async def get_answers_by_benchmark_version(
    benchmark_version_id: int,
    answer_service: AnswerService = Depends(get_answer_service),
):
    return await answer_service.get_all_by_benchmark_version(benchmark_version_id)
