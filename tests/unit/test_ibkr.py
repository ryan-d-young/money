import pytest
from aiohttp import ClientSession
from yarl import URL

from src import api

HMDS_BARS_REQUEST = {
    "conid": "265598",
    "bar_type": "Last",
    "start_time": "2024-01-01",
    "period": "6d",
    "direction": "-1",
    "bar": "5mins",
}
ISERVER_BARS_REQUEST = {
    "conid": "265598",
    "period": "6d",
    "bar": "5mins",
    "start_time": "2024-01-01",
}


@pytest.mark.asyncio
async def test_auth(api_root: URL):
    async with ClientSession() as client:
        async with client.get(
            api_root / "iserver" / "auth" / "status",
            ssl=False
        ) as response:
            assert response.status == 200
            json = await response.json()
            assert json
            assert json["connected"]
            assert json["authenticated"]
            assert not json["competing"]


# @pytest.mark.asyncio
# async def test_ibkr_hmds_historical_bars(test_session: api.core.Session):
#     async for response in test_session("ibkr", "hmds_historical_bars", **HMDS_BARS_REQUEST):
#         assert response.data
#         data = response.data
#         for key in {"timestamp", "identifier", "attribute", "open_", "high", "low", "close", "volume"}:
#             assert key in data
#         break


# @pytest.mark.asyncio
# async def test_ibkr_iserver_historical_bars(test_session: api.core.Session):
#     async for response in test_session("ibkr", "iserver_historical_bars", **ISERVER_BARS_REQUEST):
#         assert response.data
#         data = response.data
#         for key in {"timestamp", "identifier", "attribute", "open_", "high", "low", "close", "volume"}:
#             assert key in data
#         break
