from fastapi import APIRouter, Depends, HTTPException, status
from pydantic_core import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories import AnswerRepository
from schemas import AnswerReadSchema, BenchmarkVersionCreateSchema
from services import AnswerService
from services.answer import AnswerNotFound


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


@router.get(
    path="/by-benchmark-version",
    response_model=list[AnswerReadSchema],
    summary="Получить все ответы в конкретной версии бенчмарка",
)
async def get_all_by_benchmark_version(
    year: int,
    month: int,
    answer_service: AnswerService = Depends(get_answer_service),
):
    try:
        benchmark_version = BenchmarkVersionCreateSchema(year=year, month=month)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.errors()[0],
        )

    return await answer_service.get_all_by_benchmark_version(benchmark_version)
