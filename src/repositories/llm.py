from sqlalchemy.ext.asyncio import AsyncSession

from models import LLMORM

from .base import BaseRepository


class LLMRepository(BaseRepository[LLMORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(LLMORM, session)
