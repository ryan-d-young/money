from typing import AsyncGenerator

import yarl
from aiohttp import ClientSession
from pydantic import ValidationError

from src import api, util

from . import models, models_generated, tables

try:
    ROOT = (
        yarl.URL.build(
            host=util.env.get("IBKR_HOST"), port=int(util.env.get("IBKR_PORT"))
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
    requires={"client": api.dependencies.HttpClient},
)
async def hmds_historical_bars(
    client: ClientSession, request: models_generated.HmdsHistoryGetParametersQuery
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "hmds" / "history"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["data"]:
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(request.conid),
            timestamp=api.core.Timestamp(record.get("t")),
            attribute=api.core.Attribute("price"),
            data=api.core.Record(
                data={
                    "open_": record.get("o"),
                    "high": record.get("h"),
                    "low": record.get("l"),
                    "close": record.get("c"),
                    "volume": record.get("v"),
                }
            ),
        )


@api.router(
    accepts=models_generated.IserverMarketdataHistoryGetParametersQuery,
    returns=models.OHLCBar,
    stores=tables.OHLC,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_historical_bars(
    client: ClientSession,
    request: models_generated.IserverMarketdataHistoryGetParametersQuery,
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "marketdata" / "history"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["data"]:
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(request.conid),
            timestamp=api.core.Timestamp(record.get("t")),
            attribute=api.core.Attribute("price"),
            data=api.core.Record(
                data={
                    "open_": record.get("o"),
                    "high": record.get("h"),
                    "low": record.get("l"),
                    "close": record.get("c"),
                    "volume": record.get("v"),
                }
            ),
        )


@api.router(
    accepts=models_generated.Currency,
    returns=models_generated.CurrencyPairs,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_currency_pairs(
    client: ClientSession, request: models_generated.Currency
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "currency" / "pairs"
    params = {"currency": request.value}
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json[request.value]:
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(record.get("symbol")),
            timestamp=None,
            attribute=api.core.Attribute("currency_pair"),
            data=api.core.Object(
                model=models_generated.CurrencyPair,
                data={
                    "symbol": record.get("symbol"),
                    "conid": record.get("conid"),
                    "ccy_pair": record.get("ccyPair"),
                },
            ),
        )


@api.router(
    accepts=models_generated.IserverExchangerateGetParametersQuery,
    returns=models.FXSpot,
    stores=tables.FXSpot,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_exchange_rate(
    client: ClientSession,
    request: models_generated.IserverExchangerateGetParametersQuery,
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "exchangerate"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(f"{request.source}/{request.target}"),
        timestamp=api.core.Timestamp(),
        attribute=api.core.Attribute("price"),
        data=api.core.Object(
            model=models.FXSpot,
            data={
                "base": request.source,
                "terms": request.target,
                "spot": json.get("rate"),
            },
        ),
    )


@api.router(
    accepts=models_generated.TrsrvAllConidsGetParametersQuery,
    returns=models_generated.TrsrvAllConidsGetResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def trsrv_conids(
    client: ClientSession, request: models_generated.TrsrvAllConidsGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "trsrv" / "all-conids"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(record.get("symbol")),
            timestamp=api.core.Timestamp(record.get("t")),
            attribute=api.core.Attribute("conid"),
            data=api.core.Object(
                model=models_generated.TrsrvAllConidsGetResponseItem, data=record
            ),
        )


@api.router(
    accepts=models_generated.TrsrvFuturesGetParametersQuery,
    returns=models.FuturesContract,
    stores=tables.FuturesChains,
    requires={"client": api.dependencies.HttpClient},
)
async def trsrv_futures_from_symbol(
    client: ClientSession, request: models_generated.TrsrvFuturesGetParametersQuery
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "trsrv" / "futures"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for symbol in json:
        for contract in json[symbol]:
            yield api.core.Response(
                request=request,
                identifier=api.core.Identifier(symbol),
                timestamp=api.core.Timestamp(contract.get("t")),
                attribute=api.core.Attribute("futures_contract"),
                data=api.core.Object(model=models.FuturesContract, data=contract),
            )


@api.router(
    accepts=models_generated.TrsrvSecdefScheduleGetParametersQuery,
    returns=models_generated.TradingScheduleItem,
    requires={"client": api.dependencies.HttpClient},
)
async def trsrv_schedule_from_symbol(
    client: ClientSession,
    request: models_generated.TrsrvSecdefScheduleGetParametersQuery,
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "trsrv" / "secdef" / "schedule"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(record.get("symbol")),
            timestamp=api.core.Timestamp(record.get("t")),
            attribute=api.core.Attribute("schedule"),
            data=api.core.Object(
                model=models_generated.TradingScheduleItem, data=record
            ),
        )


@api.router(
    accepts=models.ContractId,
    returns=models_generated.IserverContractConidInfoAndRulesGetResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_contract_info_from_conid(
    client: ClientSession, request: models.ContractId
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "contract" / request.root / "info-and-rules"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.root),
        timestamp=None,
        attribute=api.core.Attribute("contract_info"),
        data=api.core.Object(
            model=models_generated.IserverContractConidInfoAndRulesGetResponse,
            data=json,
        ),
    )


@api.router(
    accepts=models_generated.IserverSecdefStrikesGetParametersQuery,
    returns=models.OptionsStrikes,
    stores=tables.OptionsStrikes,
)
async def iserver_strikes_from_conid(
    client: ClientSession,
    request: models_generated.IserverSecdefStrikesGetParametersQuery,
) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "secdef" / "strikes"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.conid),
        timestamp=None,
        attribute=api.core.Attribute("strikes"),
        data=api.core.Object(
            model=models.OptionsStrikes,
            data={
                "conid": request.conid,
                "sectype": request.sectype,
                "exchange": request.exchange,
                "call": json["call"],
                "put": json["put"],
            },
        ),
    )


@api.router(
    accepts=models_generated.IserverSecdefSearchGetParametersQuery,
    returns=models_generated.SecdefSearchResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_secdef_search(
    client: ClientSession,
    request: models_generated.IserverSecdefSearchGetParametersQuery,
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "secdef" / "search"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.conid),
        timestamp=None,
        attribute=api.core.Attribute("secdef_search"),
        data=api.core.Object(model=models_generated.SecdefSearchResponse, data=json),
    )


@api.router(
    returns=models_generated.GwApiV1AccountsGetResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_accounts(
    client: ClientSession,
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "accounts"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=None,
        identifier=api.core.Identifier(json.get("root")),
        timestamp=None,
        attribute=api.core.Attribute("accounts"),
        data=api.core.Object(model=models_generated.UserAccountsResponse, data=json),
    )


@api.router(
    accepts=models_generated.IserverSecdefInfoGetParametersQuery,
    returns=models_generated.SecDefInfoResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_secdef_info(
    client: ClientSession, request: models_generated.IserverSecdefInfoGetParametersQuery
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "secdef" / "info"
    params = request.model_dump()
    async with client.get(url, params=params) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.conid),
        timestamp=None,
        attribute=api.core.Attribute("secdef_info"),
        data=api.core.Object(model=models_generated.SecDefInfoResponse, data=json),
    )


@api.router(
    accepts=models.OrderId,
    returns=models_generated.OrderStatus,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_account_order_status(
    client: ClientSession, request: models.OrderId
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "account" / "order" / "status" / request.root
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.root),
        timestamp=None,
        attribute=api.core.Attribute("order_status"),
        data=api.core.Object(model=models_generated.OrderStatus, data=json),
    )


@api.router(
    returns=models_generated.OrderSubmitSuccess
    | models_generated.OrderSubmitError
    | models_generated.OrderReplyMessage
    | models_generated.AdvancedOrderReject,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_account_post_order(
    client: ClientSession, request: models.OrderPayload
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
        models_generated.AdvancedOrderReject,
    ):
        try:
            model = model_received
            instance = model(**json)
        except ValidationError:
            model = None
            continue
    if instance is None:
        raise ValueError(f"Unrecognized response format: {json}")
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.account_id),
        timestamp=None,
        attribute=api.core.Attribute("order_submit"),
        data=api.core.Object(model=model, data=instance.model_dump()),
    )


@api.router(
    requires={"client": api.dependencies.HttpClient},
    returns=models_generated.OrderCancelSuccess | models_generated.OrderSubmitError,
)
async def iserver_account_delete_order(
    client: ClientSession, request: models.CancelOrder
) -> AsyncGenerator[dict, None]:
    url = ROOT / "iserver" / "account" / request.account_id / "order" / request.order_id
    async with client.delete(url) as response:
        response.raise_for_status()
        json = await response.json()
    instance = None
    for model_received in (
        models_generated.OrderCancelSuccess,
        models_generated.OrderSubmitError,
    ):
        try:
            model = model_received
            instance = model(**json)
        except:
            continue
    if instance is None:
        raise ValueError(f"Unrecognized response format: {json}")
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.account_id),
        timestamp=None,
        attribute=api.core.Attribute("order_cancel"),
        data=api.core.Object(model=model, data=instance.model_dump()),
    )


@api.router(
    returns=models_generated.AccountAttributes,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_accounts(client: ClientSession) -> AsyncGenerator[dict, None]:
    url = ROOT / "portfolio" / "accounts"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        yield api.core.Response(
            request=None,
            identifier=api.core.Identifier(record.get("root")),
            timestamp=None,
            attribute=api.core.Attribute("account_attributes"),
            data=api.core.Object(model=models_generated.AccountAttributes, data=record),
        )


@api.router(
    accepts=models.AccountId,
    returns=models.Ledger,
    stores=tables.AccountLedger,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_account_ledger(
    client: ClientSession, request: models.AccountId
) -> AsyncGenerator[dict, None]:
    url = ROOT / "portfolio" / request.root / "ledger"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    for currency, ledger in json["root"].items():
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(request.root),
            timestamp=None,
            attribute=api.core.Attribute("account_ledger"),
            data=api.core.Object(
                model=models.Ledger, data={"currency": currency, **ledger}
            ),
        )


@api.router(
    accepts=models.AccountId,
    returns=models_generated.PortfolioSummary,
    stores=tables.AccountSummary,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_account_summary(
    client: ClientSession, request: models.AccountId
) -> AsyncGenerator[dict, None]:
    url = ROOT / "portfolio" / request.root / "summary"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    yield api.core.Response(
        request=request,
        identifier=api.core.Identifier(request.root),
        timestamp=None,
        attribute=api.core.Attribute("account_summary"),
        data=api.core.Object(model=models_generated.PortfolioSummary, data=json),
    )


@api.router(
    accepts=models.AccountId,
    returns=models_generated.IndividualPosition,
    stores=tables.AccountPositions,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_account_positions(
    client: ClientSession, request: models.AccountId
) -> AsyncGenerator[dict, None]:
    page_id = 1
    while True:
        url = ROOT / "portfolio" / request.root / "positions" / page_id
        async with client.get(url) as response:
            response.raise_for_status()
            json = await response.json()
        for record in json["root"]:
            yield api.core.Response(
                request=request,
                identifier=api.core.Identifier(request.root),
                timestamp=None,
                attribute=api.core.Attribute("account_positions"),
                data=api.core.Object(
                    model=models_generated.IndividualPosition, data=record
                ),
            )
        if len(json["root"]) < 100:
            break
        page_id += 1
