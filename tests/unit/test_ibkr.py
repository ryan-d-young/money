import pytest
from yarl import URL
from httpx import AsyncClient

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
    response = await AsyncClient(verify=False).get(str(api_root / "iserver" / "auth" / "status"))
    assert response.status_code == 200
    json = response.json()
    assert json
    assert json["connected"]
    assert json["authenticated"]
    assert not json["competing"]


@pytest.mark.asyncio
async def test_ibkr_hmds_historical_bars(ibkr_api_session: api.Session):
    async for response in ibkr_api_session("ibkr", "hmds_historical_bars", **HMDS_BARS_REQUEST):
        assert response.json
        data = response.json
        for key in {"timestamp", "identifier", "attribute", "open_", "high", "low", "close", "volume"}:
            assert key in data
        break
