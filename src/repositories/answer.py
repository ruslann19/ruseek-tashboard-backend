from sqlalchemy.ext.asyncio import AsyncSession

from models import AnswerORM

from .base import BaseRepository


class AnswerRepository(BaseRepository[AnswerORM]):
    def __init__(self, session: AsyncSession):
        super().__init__(AnswerORM, session)
