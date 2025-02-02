import pytest
import pytest_asyncio

from src.ext import ibkr


@pytest.mark.asyncio
async def test_connection(http_client):
    async with http_client.get("https://api.ibkr.com/gw/api/v1/echo/https") as response:
        assert response.status == 200
        assert await response.json() == {
            "requestMethod": "GET",
            "securityPolicy": "HTTPS",
            "queryParameters": {},
        }

