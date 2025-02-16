import pytest

from src import api


HMDS_BARS_REQUEST = {
    "conid": "265598",
    "bar_type": "Last",
    "start_time": "2024-01-01",
    "period": "6d",
    "direction": "-1",
    "bar": "5mins",
}

# @pytest.mark.asyncio
# async def test_store_bars(test_session: api.core.Session):
#     async for response in test_session("ibkr", "iserver_historical_bars", **HMDS_BARS_REQUEST):
#         ...
        
