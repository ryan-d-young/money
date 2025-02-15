import pytest
from aiohttp import ClientSession
from yarl import URL

from src import api


@pytest.mark.asyncio
async def test_connection(api_root: URL):
    async with ClientSession() as client:
        async with client.get(
            api_root / "iserver" / "accounts", 
            ssl=False
        ) as response:
            assert response.status == 200


@pytest.mark.asyncio
async def test_market_data(api_root: URL):
    async with ClientSession() as client:
        async with client.get(
            api_root / "hmds" / "history", 
            ssl=False, 
            params={
                "conid": "265598",
                "bar_type": "Last",
                "start_time": "2024-01-01",
                "period": "6d",
                "bar": "5mins",
                "direction": "-1",
            }
        ) as response:
            assert response.status == 200
            json = await response.json()
            assert json
            assert json["data"]
            assert len(json["data"]) > 0


@pytest.mark.asyncio
async def test_ibkr_hmds_historical_bars(test_session: api.core.Session):
    request = test_session(
        "ibkr", "hmds_historical_bars",
        conid="265598",
        bar_type="Last",
        start_time="2024-01-01",
        period="6d",
        direction="-1",
        bar="5mins",
    )
    async for response in request:
        assert response.data
        data = response.data
        for key in {"timestamp", "identifier", "attribute", "open_", "high", "low", "close", "volume"}:
            assert key in data
        break
    