import asyncio
import json
from typing import Literal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session_maker
from llm_clients import (
    Judge,
    LlmClient,
    LlmJudge,
    MockJudge,
    MockLlmClient,
    RouterAiClient,
)
from repositories import AnswerRepository, BenchmarkVersionRepository, TaskRepository
from schemas import (
    AnswerCreateSchema,
    AnswerUpdateSchema,
    BenchmarkVersionCreateSchema,
    BenchmarkVersionReadSchema,
    LlmReadSchema,
    TaskReadSchema,
    VerificationRequest,
    YourOwnGameMetadata,
)
from services import AnswerService, BenchmarkVersionServise, TaskServise
from utils.html_processing import get_raw_text
from utils.parse_tasks import parse_tasks

router = APIRouter(
    prefix="/ws",
    tags=["Вебсокет"],
)


@router.websocket("/parse-game")
async def collect_tasks(websocket: WebSocket):
    await websocket.accept()
    try:
        received_data = await websocket.receive_json()
        game_metadata = YourOwnGameMetadata(**received_data)

        WS_MESSAGE_ERROR = "error"
        WS_MESSAGE_TASK = "task"
        ws_message = {
            "type": None,
            "content": None,
        }

        try:
            text = get_raw_text(game_metadata.source_url)
        except Exception as error:
            ws_message["type"] = WS_MESSAGE_ERROR
            ws_message["content"] = str(error)
            await websocket.send_text(json.dumps(ws_message))
            await websocket.close()
            return

        async with async_session_maker() as session:
            repository = TaskRepository(session)
            task_service = TaskServise(repository, session)

            async for task in parse_tasks(text, game_metadata):
                added_task = await task_service.add_task(task)

                ws_message["type"] = WS_MESSAGE_TASK
                ws_message["content"] = added_task.model_dump_json()

                await websocket.send_text(json.dumps(ws_message))

        await websocket.close()
    except WebSocketDisconnect:
        pass


@router.websocket("/test-llms")
async def test_llms(websocket: WebSocket):
    await websocket.accept()

    received_data = await websocket.receive_json()

    benchmark_version = BenchmarkVersionCreateSchema(
        year=received_data["benchmark_version"]["year"],
        month=received_data["benchmark_version"]["month"],
    )

    selected_tasks = [
        TaskReadSchema(**task) for task in received_data["selected_tasks"]
    ]

    selected_llms = [LlmReadSchema(**llm) for llm in received_data["selected_llms"]]

    async with async_session_maker() as session:
        benchmark_version_repository = BenchmarkVersionRepository(session)
        benchmark_version_service = BenchmarkVersionServise(
            benchmark_version_repository, session
        )
        # TODO: убрать этот код (удаление существующих версий бенчмарка) после тестирования
        existing_versions = await benchmark_version_service.get_all()
        for version in existing_versions:
            await benchmark_version_service.delete(version.id)

        added_benchmark_version = await benchmark_version_service.add(benchmark_version)

    # TODO: вернуть реального судью
    judge = MockJudge()
    # judge = LlmJudge()
    pipelines = []

    for task in selected_tasks:
        for llm in selected_llms:
            async with async_session_maker() as session:
                pipeline = asyncio.create_task(
                    run_pipline(
                        llm_schema=llm,
                        task=task,
                        benchmark_version=added_benchmark_version,
                        judge=judge,
                        session=session,
                        websocket=websocket,
                    )
                )
                pipelines.append(pipeline)

    await asyncio.gather(*pipelines, return_exceptions=True)

    await websocket.close()

    # TODO: убрать это (удаление созданной версии бенчмарка)
    # await benchmark_version_service.delete(added_benchmark_version.id)


@router.websocket("/update-benchmark-version")
async def update_benchmark_version(websocket: WebSocket):
    await websocket.accept()

    received_data = await websocket.receive_json()

    benchmark_version = BenchmarkVersionCreateSchema(
        year=received_data["benchmark_version"]["year"],
        month=received_data["benchmark_version"]["month"],
    )

    old_tasks = [TaskReadSchema(**task) for task in received_data["old_tasks"]]
    deleted_tasks = [TaskReadSchema(**task) for task in received_data["deleted_tasks"]]
    new_tasks = [TaskReadSchema(**task) for task in received_data["new_tasks"]]

    old_llms = [LlmReadSchema(**llm) for llm in received_data["old_llms"]]
    deleted_llms = [LlmReadSchema(**llm) for llm in received_data["deleted_llms"]]
    new_llms = [LlmReadSchema(**llm) for llm in received_data["new_llms"]]

    # Удаляем то, что удалили
    async with async_session_maker() as session:
        answer_repository = AnswerRepository(session)
        answer_service = AnswerService(answer_repository, session)

        answers_for_delete = []

        for deleted_llm in deleted_llms:
            deleted_llm_answers = await answer_service.get_all_answers(
                llm_id=deleted_llm.id
            )
            answers_for_delete.extend(deleted_llm_answers)

        for deleted_task in deleted_tasks:
            deleted_task_answers = await answer_service.get_all_answers(
                task_id=deleted_task.id
            )
            answers_for_delete.extend(deleted_task_answers)

        for answer in answers_for_delete:
            await answer_service.delete_answer(answer.id)

        # Загружаем версию бенчмарка (вместе с id)
        benchmark_version_repository = BenchmarkVersionRepository(session)
        benchmark_version_service = BenchmarkVersionServise(
            benchmark_version_repository, session
        )
        loaded_benchmark_version = await benchmark_version_service.get_one_or_none(
            year=benchmark_version.year,
            month=benchmark_version.month,
        )

    # TODO: вернуть реального судью
    judge = MockJudge()
    # judge = LlmJudge()
    pipelines = []

    for task in old_tasks:
        for llm in new_llms:
            async with async_session_maker() as session:
                pipeline = asyncio.create_task(
                    run_pipline(
                        llm_schema=llm,
                        task=task,
                        benchmark_version=loaded_benchmark_version,
                        judge=judge,
                        session=session,
                        websocket=websocket,
                    )
                )
                pipelines.append(pipeline)

    filtered_old_llms = [llm for llm in old_llms if llm not in deleted_llms]
    all_testing_llms = filtered_old_llms + new_llms

    for task in new_tasks:
        for llm in all_testing_llms:
            async with async_session_maker() as session:
                pipeline = asyncio.create_task(
                    run_pipline(
                        llm_schema=llm,
                        task=task,
                        benchmark_version=loaded_benchmark_version,
                        judge=judge,
                        session=session,
                        websocket=websocket,
                    )
                )
                pipelines.append(pipeline)

    await asyncio.gather(*pipelines, return_exceptions=True)

    await websocket.close()

    # TODO: убрать это (удаление созданной версии бенчмарка)
    # await benchmark_version_service.delete(added_benchmark_version.id)


def create_question_with_header(question: str) -> str:
    filename = "./prompt_templates/question.txt"
    with open(filename) as f:
        question_template = f.read()

    content = question_template.format(question=question)
    return content


class ProgressInfo(BaseModel):
    progress_type: str = Literal["asking", "verification"]
    task_id: int
    tested_llm_id: int

    model_config = ConfigDict(from_attributes=True)


async def run_pipline(
    llm_schema: LlmReadSchema,
    task: TaskReadSchema,
    benchmark_version: BenchmarkVersionReadSchema,
    judge: Judge,
    session: AsyncSession,
    websocket: WebSocket,
) -> None:
    answer_repository = AnswerRepository(session)
    answer_service = AnswerService(answer_repository, session)

    # TODO: вернуть реального клиента
    llm_client = MockLlmClient()
    # llm_client = RouterAiClient(model=llm.llm_name)

    formatted_question = create_question_with_header(task.question)
    llm_answer = await llm_client.ask(formatted_question)

    answer = AnswerCreateSchema(
        task_id=task.id,
        llm_id=llm_schema.id,
        benchmark_version_id=benchmark_version.id,
        llm_answer=llm_answer,
    )
    added_answer = await answer_service.add_answer(answer)

    message = ProgressInfo(
        progress_type="asking",
        task_id=task.id,
        tested_llm_id=llm_schema.id,
    )
    await websocket.send_text(message.model_dump_json())

    verification_request = VerificationRequest(
        question=task.question,
        correct_answer=task.correct_answer,
        llm_answer=llm_answer,
    )
    verification_response = await judge.verify(verification_request)

    if verification_response.verdict != "FORMAT_ERROR":
        added_answer.is_correct = verification_response.verdict == "RIGHT"
        added_answer.judge_explaination = verification_response.explaination

        answer_data_for_update = AnswerUpdateSchema.model_validate(
            added_answer.model_dump()
        )
        await answer_service.update_answer(answer_data_for_update)

    message = ProgressInfo(
        progress_type="verification",
        task_id=task.id,
        tested_llm_id=llm_schema.id,
    )
    await websocket.send_text(message.model_dump_json())
