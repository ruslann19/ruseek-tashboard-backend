from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

engine = create_engine(settings.DB_URL)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
