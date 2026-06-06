import httpx
from httpx import Response

from core.config import settings


class RouterAiApi:
    def __init__(self):
        self.headers = {
            "Authorization": settings.ROUTERAI_API_KEY,
        }

    async def get(self, url: str) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=self.headers,
            )
            return response

    async def get_routerai_balance(self):
        response = await self.get("https://routerai.ru/api/v1/credits")
        credits = response.json()["data"]["credits"]
        return credits

    async def get_models(self):
        response = await self.get("https://routerai.ru/api/v1/models")
        models = response.json()["data"]
        return models
