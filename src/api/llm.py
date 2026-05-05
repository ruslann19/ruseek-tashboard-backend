from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from repositories import LLMRepository
from schemas.llm import LLMCreateSchema, LLMReadSchema, LLMUpdateSchema
from services import LLMService
from services.llm import LLMAlreadyExists, LLMNotFound

router = APIRouter(
    prefix="/llms",
    tags=["LLM"],
)


async def get_llm_repository(session: AsyncSession = Depends(get_async_session)):
    return LLMRepository(session)


async def get_llm_service(repository: LLMRepository = Depends(get_llm_repository)):
    return LLMService(repository, repository.session)


@router.post(
    "/",
    response_model=LLMReadSchema,
    summary="Добавить LLM",
)
async def create_llm(
    llm: LLMCreateSchema,
    llm_service: LLMService = Depends(get_llm_service),
):
    try:
        return await llm_service.add_llm(llm)
    except LLMAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="LLM уже существует",
        )


@router.get(
    "/",
    response_model=list[LLMReadSchema],
    summary="Список всех LLM",
)
async def get_llms(
    llm_service: LLMService = Depends(get_llm_service),
):
    return await llm_service.get_all_llms()


@router.get(
    "/{llm_id}",
    response_model=LLMReadSchema,
    summary="Данные одной LLM",
)
async def get_llm(
    llm_id: int,
    llm_service: LLMService = Depends(get_llm_service),
):
    try:
        return await llm_service.get_llm_by_id(llm_id)
    except LLMNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM не найдена",
        )


@router.put(
    "/{llm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить данные одной LLM",
)
async def update_llm(
    llm_data_for_update: LLMUpdateSchema,
    llm_service: LLMService = Depends(get_llm_service),
):
    await llm_service.update_llm(llm_data_for_update)


@router.delete(
    "/{llm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить одну LLM",
)
async def delete_llm(
    llm_id: int,
    llm_service: LLMService = Depends(get_llm_service),
):
    await llm_service.delete_llm(llm_id)
