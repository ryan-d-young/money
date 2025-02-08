import pytest
from aiohttp import ClientSession
from yarl import URL

from src.util import env
from src.ext import ibkr


@pytest.mark.asyncio
async def test_connection(api_root: URL, client: ClientSession):
    async with client.get(api_root / "iserver" / "accounts", ssl=False) as response:
        assert response.status == 200


