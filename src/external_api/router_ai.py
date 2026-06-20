import httpx
from httpx import Response
from pydantic import BaseModel

from core.config import settings


class RouterAiBalanceResponse(BaseModel):
    rubles: float


class RouterAiApi:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.ROUTERAI_API_KEY}",
        }

    async def get(self, url: str) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=self.headers,
            )
            return response

    async def get_balance(self) -> RouterAiBalanceResponse:
        response = await self.get("https://routerai.ru/api/v1/credits")
        balance = response.json()["data"]["credits"]
        response = RouterAiBalanceResponse(rubles=balance)
        return response

    async def get_models(self):
        response = await self.get("https://routerai.ru/api/v1/models")
        models = response.json()["data"]
        return models
