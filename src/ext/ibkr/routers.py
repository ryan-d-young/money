from typing import AsyncGenerator

import yarl
from aiohttp import ClientSession
from pydantic import ValidationError

from src import api, util
from . import models, models_generated, tables
from .util import unix_to_iso


try:
    ROOT = (
        yarl.URL.build(
            scheme="https", 
            host=util.env.get("IBKR_HOST"), 
            port=int(util.env.get("IBKR_PORT"))
        )
        / "v1"
        / "api"
    )
except KeyError as e:
    raise EnvironmentError("Unable to obtain IBKR credentials from environment") from e


@api.core.router.define(
    accepts=models_generated.HmdsHistoryGetParametersQuery,
    returns=models.OHLCBar,
    stores=tables.OHLC,
    requires={"client": api.dependencies.HttpClient},
)
async def hmds_historical_bars(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "hmds" / "history"
    async with client.get(url, params=request, ssl=False) as response:
        response.raise_for_status()
        json = await response.json()
    for record_in in json["data"]:
        record_out = api.core.Record(
            identifier=api.core.Identifier(request["conid"]),
            timestamp=api.core.Timestamp(unix_to_iso(record_in.get("t"))),
            attribute=api.core.Attribute("price"),
            data={
                "open_": record_in.get("o"),
                "high": record_in.get("h"),
                "low": record_in.get("l"),
                "close": record_in.get("c"),
                "volume": record_in.get("v"),
            }
        )
        yield api.core.Response(request, record_out)
                


@api.core.router.define(
    accepts=models_generated.IserverMarketdataHistoryGetParametersQuery,
    returns=models.OHLCBar,
    stores=tables.OHLC,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_historical_bars(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "marketdata" / "history"
    async with client.get(url, params=request, ssl=False) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["data"]:
        record_out = api.core.Record(
            identifier=api.core.Identifier(request["conid"]),
            timestamp=api.core.Timestamp(unix_to_iso(record.get("t"))),
            attribute=api.core.Attribute("price"),
            data={
                "open_": record.get("o"),
                "high": record.get("h"),
                "low": record.get("l"),
                "close": record.get("c"),
                "volume": record.get("v"),
            }
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.Currency,
    returns=models_generated.CurrencyPairs,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_currency_pairs(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "currency" / "pairs"
    async with client.get(url, params={"currency": request["value"]}) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json[request["value"]]:
        record_out = api.core.Object(
            identifier=api.core.Identifier(record.get("symbol")),
            timestamp=api.core.Timestamp(),
            attribute=api.core.Attribute("currency_pair"),
            model=models_generated.CurrencyPair,
                data={
                    "symbol": record.get("symbol"),
                    "conid": record.get("conid"),
                "ccy_pair": record.get("ccyPair"),
            },
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverExchangerateGetParametersQuery,
    returns=models.FXSpot,
    stores=tables.FXSpot,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_exchange_rate(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "exchangerate"
    async with client.get(url, params={"source": request["source"], "target": request["target"]}) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(".".join([request["source"], request["target"]])),
        timestamp=api.core.Timestamp(),
        attribute=api.core.Attribute("price"),
        model=models.FXSpot,
        data={
            "base": request["source"],
            "terms": request["target"],
            "spot": json.get("rate"),
        },
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.TrsrvAllConidsGetParametersQuery,
    returns=models_generated.TrsrvAllConidsGetResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def trsrv_conids(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "trsrv" / "all-conids"
    async with client.get(url, params=request) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        record_out = api.core.Object(
            identifier=api.core.Identifier(record.get("symbol")),
            timestamp=api.core.Timestamp(record.get("t")),
            attribute=api.core.Attribute("conid"),
            model=models_generated.TrsrvAllConidsGetResponseItem,
            data=record,
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.TrsrvFuturesGetParametersQuery,
    returns=models.FuturesContract,
    stores=tables.FuturesChains,
    requires={"client": api.dependencies.HttpClient},
)
async def trsrv_futures_from_symbol(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "trsrv" / "futures"
    async with client.get(url, params=request) as response:
        response.raise_for_status()
        json = await response.json()
    for symbol in json:
        for contract in json[symbol]:
            record_out = api.core.Object(
                identifier=api.core.Identifier(symbol),
                timestamp=api.core.Timestamp(contract.get("t")),
                attribute=api.core.Attribute("futures_contract"),
                model=models.FuturesContract,
                data=contract,
            )
            yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.TrsrvSecdefScheduleGetParametersQuery,
    returns=models_generated.TradingScheduleItem,
    requires={"client": api.dependencies.HttpClient},
)
async def trsrv_schedule_from_symbol(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "trsrv" / "secdef" / "schedule"
    async with client.get(url, params=request) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        yield api.core.Response(
            request=request,
            identifier=api.core.Identifier(record.get("symbol")),
            timestamp=api.core.Timestamp(record.get("t")),
            attribute=api.core.Attribute("schedule"),
            model=models_generated.TradingScheduleItem,
            data=record,
        )


@api.core.router.define(
    accepts=models.ContractId,
    returns=models_generated.IserverContractConidInfoAndRulesGetResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_contract_info_from_conid(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "contract" / request["root"] / "info-and-rules"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(request.root),
        timestamp=None,
        attribute=api.core.Attribute("contract_info"),
        model=models_generated.IserverContractConidInfoAndRulesGetResponse,
        data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverSecdefStrikesGetParametersQuery,
    returns=models.OptionsStrikes,
    stores=tables.OptionsStrikes,
)
async def iserver_strikes_from_conid(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "secdef" / "strikes"
    async with client.get(url, params=request) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(request["conid"]),
        timestamp=None,
        attribute=api.core.Attribute("strikes"),
        model=models.OptionsStrikes,
        data={
            "conid": request["conid"],
            "sectype": request["sectype"],
            "exchange": request["exchange"],
            "call": json["call"],
            "put": json["put"],
        },
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverSecdefSearchGetParametersQuery,
    returns=models_generated.SecdefSearchResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_secdef_search(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "secdef" / "search"
    async with client.get(url, params=request) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(request["conid"]),
        timestamp=None,
        attribute=api.core.Attribute("secdef_search"),
        model=models_generated.SecdefSearchResponse,
        data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    returns=models_generated.GwApiV1AccountsGetResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_accounts(client: ClientSession) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "accounts"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(json.get("root")),
        timestamp=None,
        attribute=api.core.Attribute("accounts"),
        model=models_generated.UserAccountsResponse,
        data=json,
    )
    yield api.core.Response(None, record_out)


@api.core.router.define(
    accepts=models_generated.IserverSecdefInfoGetParametersQuery,
    returns=models_generated.SecDefInfoResponse,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_secdef_info(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "secdef" / "info"
    async with client.get(url, params=request) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(request["conid"]),
        timestamp=None,
        attribute=api.core.Attribute("secdef_info"),
        model=models_generated.SecDefInfoResponse,
        data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.OrderId,
    returns=models_generated.OrderStatus,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_account_order_status(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "account" / "order" / "status" / request["root"]
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(request.root),
        timestamp=None,
        attribute=api.core.Attribute("order_status"),
        model=models_generated.OrderStatus,
        data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.OrderPayload,
    returns=models_generated.OrderSubmitSuccess
    | models_generated.OrderSubmitError
    | models_generated.OrderReplyMessage
    | models_generated.AdvancedOrderReject,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_account_post_order(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "account" / request["account_id"] / "orders"
    async with client.post(url, payload=request) as response:
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
    record_out = api.core.Object(
        identifier=api.core.Identifier(request["account_id"]),
        timestamp=None,
        attribute=api.core.Attribute("order_submit"),
        model=model,
        data=instance.model_dump(),
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.CancelOrder,
    returns=models_generated.OrderCancelSuccess | models_generated.OrderSubmitError,
    requires={"client": api.dependencies.HttpClient},
)
async def iserver_account_delete_order(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "iserver" / "account" / request["account_id"] / "order" / request["order_id"]
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
        except ValidationError:
            model = None
            continue
    if instance is None:
        raise ValueError(f"Unrecognized response format: {json}")
    record_out = api.core.Object(
        identifier=api.core.Identifier(request["account_id"]),
        timestamp=None,
        attribute=api.core.Attribute("order_cancel"),
        model=model,
        data=instance.model_dump(),
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    returns=models_generated.AccountAttributes,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_accounts(client: ClientSession) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "portfolio" / "accounts"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    for record in json["root"]:
        record_out = api.core.Object(
            identifier=api.core.Identifier(record.get("root")),
            timestamp=None,
            attribute=api.core.Attribute("account_attributes"),
            model=models_generated.AccountAttributes,
            data=record,
        )
        yield api.core.Response(None, record_out)

@api.core.router.define(
    accepts=models.AccountId,
    returns=models.Ledger,
    stores=tables.AccountLedger,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_account_ledger(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "portfolio" / request["root"] / "ledger"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    for currency, ledger in json["root"].items():
        record_out = api.core.Object(
            identifier=api.core.Identifier(request["root"]),
            timestamp=None,
            attribute=api.core.Attribute("account_ledger"),
            model=models.Ledger,
            data={"currency": currency, **ledger},
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.AccountId,
    returns=models_generated.PortfolioSummary,
    stores=tables.AccountSummary,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_account_summary(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    url = ROOT / "portfolio" / request["root"] / "summary"
    async with client.get(url) as response:
        response.raise_for_status()
        json = await response.json()
    record_out = api.core.Object(
        identifier=api.core.Identifier(request["root"]),
        timestamp=None,
        attribute=api.core.Attribute("account_summary"),
        model=models_generated.PortfolioSummary,
        data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.AccountId,
    returns=models_generated.IndividualPosition,
    stores=tables.AccountPositions,
    requires={"client": api.dependencies.HttpClient},
)
async def portfolio_account_positions(client: ClientSession, **request) -> AsyncGenerator[api.core.Response, None]:
    page_id = 1
    while True:
        url = ROOT / "portfolio" / request["root"] / "positions" / page_id
        async with client.get(url) as response:
            response.raise_for_status()
            json = await response.json()
        for record in json["root"]:
            record_out = api.core.Object(
                identifier=api.core.Identifier(request["root"]),
                timestamp=None,
                attribute=api.core.Attribute("account_positions"),
                model=models_generated.IndividualPosition,
                data=record,
            )
            yield api.core.Response(request, record_out)
        if len(json["root"]) < 100:
            break
        page_id += 1
