import pytest
import pytest_asyncio
from aiohttp import ClientSession

from src.util import env
from src.ext import ibkr


@pytest.mark.asyncio
async def test_connection(http_client: ClientSession, env: dict[str, str]):
    async with http_client.get("https://localhost:5000/v1/api/iserver/account/U14722285/summary", ssl=False) as response:
        assert response.status == 200
        js = await response.json()

        for k in {"accountType", "status", "balance", "SMA", "cashBalances"}:
            assert k in js  


