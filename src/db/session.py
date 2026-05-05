from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings

engine = create_async_engine(settings.DB_URL)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
