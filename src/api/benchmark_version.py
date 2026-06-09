from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_async_session
from schemas import BenchmarkVersionCreateSchema, BenchmarkVersionReadSchema
from services import BenchmarkVersionService

router = APIRouter(
    prefix="/benchmark-versions",
    tags=["Версии бенчмарка"],
)


async def get_benchmark_version_service(
    session: AsyncSession = Depends(get_async_session),
):
    return BenchmarkVersionService(session)


@router.get(
    path="",
    response_model=list[BenchmarkVersionReadSchema],
    summary="Получить список существующих версий бенчмарка",
)
async def get_benchmark_versions(
    benchmark_version_service: BenchmarkVersionService = Depends(
        get_benchmark_version_service
    ),
):
    versions = await benchmark_version_service.get_all()
    return sorted(versions)


@router.get(
    path="/potential",
    response_model=list[BenchmarkVersionCreateSchema],
    summary="Получить список потенциальных версий бенчмарка",
)
async def get_potential_versions(
    benchmark_version_service: BenchmarkVersionService = Depends(
        get_benchmark_version_service
    ),
):
    versions = await benchmark_version_service.get_potential_versions()
    return sorted(versions)


@router.delete(
    path="/{benchmark_version_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить версию бенчмарка",
)
async def delete_benchmark_version(
    benchmark_version_id: int,
    benchmark_version_service: BenchmarkVersionService = Depends(
        get_benchmark_version_service
    ),
):
    await benchmark_version_service.delete(benchmark_version_id)
