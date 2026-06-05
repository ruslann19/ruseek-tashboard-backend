import json
from collections.abc import AsyncIterator
from typing import Any

from openai import AsyncOpenAI

from core.config import settings
from schemas.task import TaskCreateCoreSchema


async def parse_tasks(
    text: str,
    metadata: dict[str, Any],
) -> AsyncIterator[TaskCreateCoreSchema]:
    with open("./prompt_templates/parse_game.txt") as f:
        parse_game_prompt = f.read()

    client = AsyncOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )

    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": parse_game_prompt},
            {"role": "user", "content": text},
        ],
        stream=True,
    )

    MAX_BUFFER_SIZE = 10 * 1024  # Ограничение 10 КБ на одну строку для безопасности

    buffer = ""
    async for chunk in response:
        text = chunk.choices[0].delta.content or ""
        buffer += text

        # Защита от бесконечного накопления текста без \n
        if len(buffer) > MAX_BUFFER_SIZE:
            raise ValueError(
                "Буфер переполнен: LLM генерирует текст без переносов строк."
            )

        # Обрабатываем буфер при появлении переноса строки
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()

            if line:
                try:
                    task_json = json.loads(line)
                    task = TaskCreateCoreSchema(
                        question=task_json["question"],
                        correct_answer=task_json["answer"],
                        published_date=metadata["published_date"],
                        source_url=metadata["source_url"],
                    )
                    yield task  # Отдаем готовую задачу в вызывающий код
                except json.JSONDecodeError:
                    continue  # Игнорируем битые строки

    remaining_line = buffer.strip()
    if remaining_line:
        try:
            task_json = json.loads(line)
            task = TaskCreateCoreSchema(
                question=task_json["question"],
                correct_answer=task_json["answer"],
                published_date=metadata["published_date"],
                source_url=metadata["source_url"],
            )
            yield task  # Отдаем готовую задачу в вызывающий код
        except json.JSONDecodeError:
            pass  # Если на конце остался мусор, просто игнорируем его
