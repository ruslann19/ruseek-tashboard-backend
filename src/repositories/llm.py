from sqlalchemy.ext.asyncio import AsyncSession

from models import LLMOrm

from .base import BaseRepository


class LLMRepository(BaseRepository[LLMOrm]):
    def __init__(self, session: AsyncSession):
        super().__init__(LLMOrm, session)
