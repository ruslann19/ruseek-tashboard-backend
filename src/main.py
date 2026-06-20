from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import (
    answer_router,
    balance_router,
    benchmark_version_router,
    llm_router,
    task_router,
    ws_router,
)
from core.config import settings
from db.session import engine
from models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(task_router)
app.include_router(llm_router)
app.include_router(answer_router)
app.include_router(ws_router)
app.include_router(balance_router)
app.include_router(benchmark_version_router)

origins = ["http://localhost:9000", settings.FRONTEND_HOST]

print(origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
)
