import asyncio
import json
from typing import Literal

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict

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
                answer_repository = AnswerRepository(session)
                answer_service = AnswerService(answer_repository, session)

                # TODO: вернуть реального клиента
                llm_client = MockLlmClient()
                # llm_client = RouterAiClient(model=llm.llm_name)

                pipeline = asyncio.create_task(
                    run_pipline(
                        llm_schema=llm,
                        llm_client=llm_client,
                        task=task,
                        benchmark_version=added_benchmark_version,
                        judge=judge,
                        answer_service=answer_service,
                        websocket=websocket,
                    )
                )
                pipelines.append(pipeline)

    await asyncio.gather(*pipelines, return_exceptions=True)

    await websocket.close()

    # TODO: убрать это (удаление созданной версии бенчмарка)
    await benchmark_version_service.delete(added_benchmark_version.id)


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
    llm_client: LlmClient,
    task: TaskReadSchema,
    benchmark_version: BenchmarkVersionReadSchema,
    judge: Judge,
    answer_service: AnswerService,
    websocket: WebSocket,
) -> None:
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
