import pytest
from aiohttp import ClientSession
from yarl import URL

from src import api
from src.ext.ibkr import models_generated

@pytest.mark.asyncio
async def test_connection(api_root: URL, client: ClientSession):
    async with client.get(api_root / "iserver" / "accounts", ssl=False) as response:
        assert response.status == 200


@pytest.mark.asyncio
async def test_ibkr_hmds_historical_bars(session: api.core.Session):
    router = session.router("ibkr", "hmds.historical_bars")
    request = api.core.Request(models_generated.HmdsHistoryGetParametersQuery)
    request.make(
        conid="265598",
        bar_type="Last",
        start_time="2024-01-01",
        period="6d",
        direction="-1",
        bar="5mins",
        outside_rth=False
    )
    
    async for response in router(request):
        assert response.status == 200
        
