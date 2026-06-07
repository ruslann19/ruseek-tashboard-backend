from fastapi import APIRouter

from external_api import (
    DeepSeekApi,
    DeepSeekBalanceResponse,
    RouterAiApi,
    RouterAiBalanceResponse,
)

router = APIRouter(
    prefix="/balance",
    tags=["Баланс"],
)


@router.get(
    "/router-ai",
    response_model=RouterAiBalanceResponse,
    summary="Получить баланс RouterAI",
)
async def get_router_ai_balance():
    router_ai_api = RouterAiApi()
    balance = await router_ai_api.get_balance()
    return balance


@router.get(
    "/deepseek",
    response_model=DeepSeekBalanceResponse,
    summary="Получить баланс DeepSeek",
)
async def get_deepseek_balance():
    deepseek_api = DeepSeekApi()
    balance = await deepseek_api.get_balance()
    return balance
