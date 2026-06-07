import httpx
from httpx import Response
from pydantic import BaseModel

from core.config import settings


class DeepSeekBalanceResponse(BaseModel):
    yuan: float
    rubles: float


class DeepSeekApi:
    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        }

    async def get(self, url: str) -> Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url,
                headers=self.headers,
            )
            return response

    async def get_balance(self):
        response = await self.get("https://api.deepseek.com/user/balance")

        balance_infos = response.json()["balance_infos"]

        for balance_info in balance_infos:
            if balance_info["currency"] == "CNY":
                total_balance = float(balance_info["total_balance"])
                break

        CURRENT_EXCHANGE_RATE = 10.61

        response = DeepSeekBalanceResponse(
            yuan=total_balance,
            rubles=total_balance * CURRENT_EXCHANGE_RATE,
        )
        return response
