from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import llm_router, task_router
from db.session import engine
from models import Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(router=task_router)
app.include_router(router=llm_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)
