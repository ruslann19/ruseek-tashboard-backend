from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from external_api import RouterAiApi
from repositories import LlmRepository
from schemas.llm import LlmCreateSchema, LlmReadSchema, LlmUpdateSchema
from services import LlmService
from services.llm import LlmAlreadyExists, LlmNotFound

router = APIRouter(
    prefix="/llms",
    tags=["LLM"],
)


async def get_llm_repository(session: AsyncSession = Depends(get_async_session)):
    return LlmRepository(session)


async def get_llm_service(repository: LlmRepository = Depends(get_llm_repository)):
    return LlmService(repository, repository.session)


@router.post(
    "/",
    response_model=LlmReadSchema,
    summary="Создать новую Llm",
)
async def create_llm(
    llm: LlmCreateSchema,
    llm_service: LlmService = Depends(get_llm_service),
):
    try:
        router_ai_api = RouterAiApi()
        router_ai_models = await router_ai_api.get_models()
        router_ai_models_ids = [model["id"] for model in router_ai_models]

        # gigachat_models = ["GigaChat-2", "GigaChat-2-Pro", "GigaChat-2-Max"]

        if llm.llm_name not in router_ai_models_ids:
            raise ValueError("Данная модель не поддерживается")

        return await llm_service.add_llm(llm)
    except LlmAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="LLM уже существует",
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=str(error),
        )


@router.get(
    "/",
    response_model=list[LlmReadSchema],
    summary="Получить все LLM",
)
async def get_llms(
    llm_service: LlmService = Depends(get_llm_service),
):
    return await llm_service.get_all_llms()


@router.get(
    "/{llm_id}",
    response_model=LlmReadSchema,
    summary="Получить конкретную LLM по ID",
)
async def get_llm(
    llm_id: int,
    llm_service: LlmService = Depends(get_llm_service),
):
    try:
        return await llm_service.get_llm_by_id(llm_id)
    except LlmNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM не найдена",
        )


@router.put(
    "/{llm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Обновить конкретную LLM по ID",
)
async def update_llm(
    llm_data_for_update: LlmUpdateSchema,
    llm_service: LlmService = Depends(get_llm_service),
):
    await llm_service.update_llm(llm_data_for_update)


@router.delete(
    "/{llm_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить конкретную LLM по ID",
)
async def delete_llm(
    llm_id: int,
    llm_service: LlmService = Depends(get_llm_service),
):
    await llm_service.delete_llm(llm_id)
