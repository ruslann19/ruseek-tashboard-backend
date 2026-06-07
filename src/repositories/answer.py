from sqlalchemy.ext.asyncio import AsyncSession

from models import AnswerOrm

from .base import BaseRepository


class AnswerRepository(BaseRepository[AnswerOrm]):
    def __init__(self, session: AsyncSession):
        super().__init__(AnswerOrm, session)
