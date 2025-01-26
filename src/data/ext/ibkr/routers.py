from typing import AsyncGenerator

import yarl
from aiohttp import ClientSession
from pydantic import ValidationError

from src.data import api
from . import models_generated, models, tables

ROOT = yarl.URL("https://api.ibkr.com/v1/api/").build()


@api.router.define(
    accepts=models_generated.HmdsHistoryGetParametersQuery,
    stores=tables.OHLC,
    requires={"client": api.dependencies.ClientSession},
)
async def hmds_historical_bars(
    client: ClientSession, 
    request: models_generated.HmdsHistoryGetParametersQuery
) -> AsyncGenerator[dict, None, None]:
    url = ROOT / "hmds" / "history"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
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
    

@api.router.define(
    accepts=models_generated.IserverMarketdataHistoryGetParametersQuery,
    stores=tables.OHLC,
    requires={"client": api.dependencies.ClientSession}
)
async def iserver_historical_bars(
    client: ClientSession, 
    request: models_generated.IserverMarketdataHistoryGetParametersQuery
) -> AsyncGenerator[dict, None, None]:
    url = ROOT / "iserver" / "marketdata" / "history"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
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


async def iserver_account_order_status(client: ClientSession, request: models.OrderId):
    url = ROOT / "iserver" / "account" / "order" / "status" / request.root



@api.router.define(
    requires={"client": api.dependencies.ClientSession},
    returns=models_generated.OrderSubmitSuccess | models_generated.OrderSubmitError | 
    models_generated.OrderReplyMessage | models_generated.AdvancedOrderReject
)
async def iserver_account_post_order(client: ClientSession, request: models.OrderPayload):
    url = ROOT / "iserver" / "account" / request.account_id / "orders"
    payload = request.model_dump()
    async with client.post(url, payload=payload) as response:
        json = await response.json()
    for model in (
        models_generated.OrderSubmitSucces, 
        models_generated.OrderSubmitError, 
        models_generated.OrderReplyMessage, 
        models_generated.AdvancedOrderReject
    ):
        try:
            yield model(**json)
        except ValidationError:
            continue
    raise ValueError(f"Unrecognized response format: {json}")


@api.router.define(
    requires={"client": api.dependencies.ClientSession},
    returns=models_generated.OrderCancelSuccess | models_generated.OrderSubmitError
)
async def iserver_account_delete_order(client: ClientSession, request: models.CancelOrder):
    url = ROOT / "iserver" / "account" / request.account_id / "order" / request.order_id
    async with client.delete(url) as response:
        json = await response.json()
    for model in (models_generated.OrderCancelSuccess, models_generated.OrderSubmitError):
        try:
            return model(**json)
        except:
            continue
    raise ValueError(f"Unrecognized response format: {json}")


@api.router.define(
    requires={"client": api.dependencies.ClientSession},
    returns=models_generated.AccountAttributes
)
async def portfolio_accounts(client: ClientSession):
    url = ROOT / "portfolio" / "accounts"
    async with client.get(url) as response:
        json = await response.json()
    for record in json["root"]:
        yield (
            models_generated
            .AccountAttributes(**record)
            .model_dump(by_alias=True)
        )


@api.router.define(
    accepts=models.AccountId,
    returns=models.Ledger,
    stores=tables.AccountLedger,
    requires={"client": api.dependencies.ClientSession}
)
async def portfolio_account_ledger(
    client: ClientSession, 
    request: models.AccountId
):
    url = ROOT / "portfolio" / request.root / "ledger"
    async with client.get(url) as response:
        json = await response.json()
    for currency, ledger in json["root"].items():
        yield {"_ledger": models.Ledger(currency=currency, **ledger)}


@api.router.define(
    accepts=models.AccountId,
    returns=models_generated.PortfolioSummary,
    stores=tables.AccountSummary,
    requires={"client": api.dependencies.ClientSession}    
)
async def portfolio_account_summary(
    client: ClientSession, 
    request: models.AccountId    
):
    url = ROOT / "portfolio" / request.root / "summary"
    async with client.get(url) as response:
        json = await response.json()
    yield json


@api.router.define(
    accepts=models.AccountId,
    returns=models_generated.IndividualPosition,
    stores=tables.AccountPositions,
    requires={"client": api.dependencies.ClientSession}
)
async def portfolio_account_positions(client: ClientSession, request: models.AccountId):
    page_id = 1
    while True:
        url = ROOT / "portfolio" / request.root / "positions" / page_id
        async with client.get(url) as response:
            json = await response.json()
        for record in json["root"]:
            yield models_generated.IndividualPosition(**record)
        if len(json["root"]) < 100:
            break
        page_id += 1
        