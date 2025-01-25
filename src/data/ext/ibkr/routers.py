from aiohttp.client import ClientResponse

from src.money import core
from src.money.deps import http
from . import data, models


@core.route(
    accepts=data.HmdsHistoricalRequest,
    returns=models.HmdsHistoryResponse,
    storage=data.store_historical_bar_response,
    depends_on=[http.ClientSession],
)
async def hmds_historical_bars(client: http.ClientSession, **kwargs) -> ClientResponse:
    async with client.request(**kwargs) as response:
        return await response


@core.route(
    accepts=data.IserverHistoricalRequest,
    returns=data.BarRecord,
    storage=data.store_historical_bar_response,
    depends_on=[http.ClientSession]
)
async def iserver_historical_bars(client: http.ClientSession, **kwargs) -> ClientResponse:
    async with client.request(**kwargs) as response:
        return await response


@core.route(
    
)
async def iserver_contracts_from_symbol():
    ...


async def trsrv_futures_from_symbol():
    ...


async def trsrv_schedule_from_symbol():
    ...


async def iserver_contract_info_from_conid():
    ...


async def iserver_strikes_from_conid():
    ...


async def iserver_secdef_from_conids():
    ...


async def iserver_secdef_search():
    ...
