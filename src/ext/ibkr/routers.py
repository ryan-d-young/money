from typing import AsyncGenerator

import yarl
from aiohttp import ClientSession
from pydantic import ValidationError

from src import api, util
from . import models_generated, models, tables

try:
    ROOT = (
        yarl.URL.build(
            host=util.env.get("IBKR_HOST"), 
            port=int(util.env.get("IBKR_PORT"))
        )
        / "v1"
        / "api"
    )  
except KeyError as e:
    raise EnvironmentError("Unable to obtain IBKR credentials from environment") from e


@api.router(
    accepts=models_generated.HmdsHistoryGetParametersQuery,
    returns=models.OHLCBar,
    stores=tables.OHLC,
    requires={"client": api.dependencies.ClientSession},
)
async def hmds_historical_bars(
    client: ClientSession, 
    request: models_generated.HmdsHistoryGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "hmds" / "history"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["data"]:
        yield {
            "timestamp": record.get("t"),
            "symbol": request.conid, 
            "open": record.get("o"),
            "high": record.get("h"),
            "low": record.get("l"),
            "close": record.get("c")
        }
    

@api.router(
    accepts=models_generated.IserverMarketdataHistoryGetParametersQuery,
    returns=models.OHLCBar,
    stores=tables.OHLC,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_historical_bars(
    client: ClientSession, 
    request: models_generated.IserverMarketdataHistoryGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "marketdata" / "history"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["data"]:
        yield {
            "timestamp": record.get("t"),
            "symbol": request.conid, 
            "open": record.get("o"),
            "high": record.get("h"),
            "low": record.get("l"),
            "close": record.get("c")
        }


@api.router(
    accepts=models_generated.Currency,
    returns=models_generated.CurrencyPairs,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_currency_pairs(
    client: ClientSession, 
    request: models_generated.Currency
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "currency" / "pairs"
    params = {"currency": request.value}
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models_generated.IserverExchangerateGetParametersQuery,
    returns=models.FXSpot,
    stores=tables.FXSpot,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_exchange_rate(
    client: ClientSession, 
    request: models_generated.IserverExchangerateGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "exchangerate"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models_generated.TrsrvAllConidsGetParametersQuery,
    returns=models_generated.TrsrvAllConidsGetResponse,
    requires={"client": api.dependencies.ClientSession}    
)
async def trsrv_conids(
    client: ClientSession, 
    request: models_generated.TrsrvAllConidsGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "trsrv" / "all-conids"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield json    


@api.router(
    accepts=models_generated.TrsrvFuturesGetParametersQuery,
    returns=models.FuturesContract,
    stores=tables.FuturesChains,
    requires={"client": api.dependencies.ClientSession}
)
async def trsrv_futures_from_symbol(
    client: ClientSession, 
    request: models_generated.TrsrvFuturesGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "trsrv" / "futures"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for symbol in json:
        for contract in json[symbol]:
            yield contract


@api.router(
    accepts=models_generated.TrsrvSecdefScheduleGetParametersQuery,
    returns=models_generated.TradingSchedule,
    requires={"client": api.dependencies.ClientSession}
)
async def trsrv_schedule_from_symbol(
    client: ClientSession, 
    request: models_generated.TrsrvSecdefScheduleGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "trsrv" / "secdef" / "schedule"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models.ContractId,
    returns=models_generated.IserverContractConidInfoAndRulesGetResponse,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_contract_info_from_conid(
    client: ClientSession, 
    request: models.ContractId
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "contract" / request.root / "info-and-rules"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models_generated.IserverSecdefStrikesGetParametersQuery,
    returns=models.OptionsStrikes,
    stores=tables.OptionsStrikes
)
async def iserver_strikes_from_conid(
    client: ClientSession, 
    request: models_generated.IserverSecdefStrikesGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "secdef" / "strikes"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield {
        "conid": request.conid,
        "sectype": request.sectype,
        "exchange": request.exchange,
        "call": json["call"],
        "put": json["put"]
    }


@api.router(
    accepts=models_generated.IserverSecdefSearchGetParametersQuery,
    returns=models_generated.SecdefSearchResponse,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_secdef_search(
    client: ClientSession, 
    request: models_generated.IserverSecdefSearchGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "secdef" / "search"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    returns=models_generated.IserverAccountsGetResponse,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_accounts(
    client: ClientSession, 
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "accounts"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models_generated.IserverSecdefInfoGetParametersQuery,
    returns=models_generated.SecDefInfoResponse,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_secdef_info(
    client: ClientSession, 
    request: models_generated.IserverSecdefInfoGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "secdef" / "info"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models.OrderId,
    returns=models_generated.OrderStatus,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_account_order_status(
    client: ClientSession, 
    request: models.OrderId
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "account" / "order" / "status" / request.root
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    returns=models_generated.OrderSubmitSuccess | models_generated.OrderSubmitError | 
    models_generated.OrderReplyMessage | models_generated.AdvancedOrderReject,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_account_post_order(
    client: ClientSession, 
    request: models.OrderPayload
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "account" / request.account_id / "orders"
    payload = request.model_dump()
    async with client.post(url, payload=payload) as response:
        response.raise_for_status()
        json = await response.json()
    instance = None
    for model_received in (
        models_generated.OrderSubmitSuccess, 
        models_generated.OrderSubmitError, 
        models_generated.OrderReplyMessage, 
        models_generated.AdvancedOrderReject
    ):
        try:
            model = model_received
            instance = model(**json)
        except ValidationError:
            model = None
            continue
    if instance is None:
        raise ValueError(f"Unrecognized response format: {json}")
    yield model, instance.model_dump()


@api.router(
    requires={"client": api.dependencies.ClientSession},
    returns=models_generated.OrderCancelSuccess | models_generated.OrderSubmitError
)
async def iserver_account_delete_order(
    client: ClientSession, 
    request: models.CancelOrder
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "account" / request.account_id / "order" / request.order_id
    async with client.delete(url) as response:
        response.raise_for_status()
        json = await response.json()
    for model in (models_generated.OrderCancelSuccess, models_generated.OrderSubmitError):
        try:
            yield model(**json)
            return
        except:
            continue
    raise ValueError(f"Unrecognized response format: {json}")


@api.router(
    requires={"client": api.dependencies.ClientSession},
    returns=models_generated.AccountAttributes
)
async def portfolio_accounts(client: ClientSession) -> AsyncGenerator[dict, None]:
    url = ROOT / "portfolio" / "accounts"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        yield (
            models_generated
            .AccountAttributes(**record)
            .model_dump(by_alias=True)
        )


@api.router(
    accepts=models.AccountId,
    returns=models.Ledger,
    stores=tables.AccountLedger,
    requires={"client": api.dependencies.ClientSession}
)
async def portfolio_account_ledger(
    client: ClientSession, 
    request: models.AccountId
) -> AsyncGenerator[dict, None]:
    url = ROOT / "portfolio" / request.root / "ledger"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    for currency, ledger in json["root"].items():
        yield {"_ledger": models.Ledger(currency=currency, **ledger)}


@api.router(
    accepts=models.AccountId,
    returns=models_generated.PortfolioSummary,
    stores=tables.AccountSummary,
    requires={"client": api.dependencies.ClientSession}    
)
async def portfolio_account_summary(
    client: ClientSession, 
    request: models.AccountId    
) -> AsyncGenerator[dict, None]:
    url = ROOT / "portfolio" / request.root / "summary"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield json


@api.router(
    accepts=models.AccountId,
    returns=models_generated.IndividualPosition,
    stores=tables.AccountPositions,
    requires={"client": api.dependencies.ClientSession}
)
async def portfolio_account_positions(
    client: ClientSession, 
    request: models.AccountId
) -> AsyncGenerator[dict, None]:
    page_id = 1
    while True:
        url = ROOT / "portfolio" / request.root / "positions" / page_id
        async with client.get(url) as response:
            response.raise_for_status()
            json = await response.json()
        for record in json["root"]:
            yield models_generated.IndividualPosition(**record)
        if len(json["root"]) < 100:
            break
        page_id += 1
        