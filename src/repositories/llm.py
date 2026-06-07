from sqlalchemy.ext.asyncio import AsyncSession

from models import LlmOrm

from .base import BaseRepository


class LlmRepository(BaseRepository[LlmOrm]):
    def __init__(self, session: AsyncSession):
        super().__init__(LlmOrm, session)
