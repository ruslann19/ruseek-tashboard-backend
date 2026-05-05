from sqlalchemy.orm import Session

from models import TaskORM

from .base import BaseRepository


class TaskRepository(BaseRepository[TaskORM]):
    def __init__(self, session: Session):
        super().__init__(TaskORM, session)
