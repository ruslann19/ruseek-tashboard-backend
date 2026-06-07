from sqlalchemy.ext.asyncio import AsyncSession

from models import BenchmarkVersionOrm

from .base import BaseRepository


class BenchmarkVersionRepository(BaseRepository[BenchmarkVersionOrm]):
    def __init__(self, session: AsyncSession):
        super().__init__(BenchmarkVersionOrm, session)
