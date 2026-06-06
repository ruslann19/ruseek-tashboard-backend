import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from db.session import async_session_maker
from repositories import TaskRepository
from schemas.your_own_game import YourOwnGameMetadata
from services import TaskServise
from utils.html_processing import get_raw_text
from utils.parse_tasks import parse_tasks

router = APIRouter(
    prefix="/ws",
    tags=["Вебсокет"],
)


@router.websocket("/")
async def collect_tasks(
    websocket: WebSocket,
):
    await websocket.accept()
    try:
        received_data = await websocket.receive_json()
        game_metadata = YourOwnGameMetadata(**received_data)

        # with open("./temporary_files/game_example.txt", "r") as f:
        #     text = f.read()

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
