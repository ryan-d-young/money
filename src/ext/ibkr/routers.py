import yarl
from httpx import AsyncClient
from pydantic import ValidationError

from src import api, util
from . import models, models_generated, tables
from .util import unix_to_iso


try:
    ROOT = (
        yarl.URL.build(
            scheme="https",
            host=util.context.env().get("IBKR_HOST"),
            port=int(util.context.env().get("IBKR_PORT")),
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
    requires={"client": api.core.deps.http.HttpClient},
)
async def hmds_historical_bars(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "hmds" / "history"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    for record_in in json["data"]:
        record_out_data = {
            "open_": record_in.get("o"),
            "high": record_in.get("h"),
            "low": record_in.get("l"),
            "close": record_in.get("c"),
            "volume": record_in.get("v"),
        }
        record_out = api.core.Record(
            identifier=api.core.symbols.Identifier(request["conid"]),
            timestamp=api.core.symbols.Timestamp(unix_to_iso(record_in.get("t"))),
            attribute=api.core.symbols.Attribute("price"),
            _data=record_out_data,
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverMarketdataHistoryGetParametersQuery,
    returns=models.OHLCBar,
    stores=tables.OHLC,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_historical_bars(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "marketdata" / "history"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    for record in json["data"]:
        record_out_data = {
            "open_": record.get("o"),
            "high": record.get("h"),
            "low": record.get("l"),
            "close": record.get("c"),
            "volume": record.get("v"),
        }
        record_out = api.core.Record(
            identifier=api.core.symbols.Identifier(request["conid"]),
            timestamp=api.core.symbols.Timestamp(unix_to_iso(record.get("t"))),
            attribute=api.core.symbols.Attribute("price"),
            _data=record_out_data,
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.Currency,
    returns=models_generated.CurrencyPairs,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_currency_pairs(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "currency" / "pairs"
    response = await client.get(str(url), params={"currency": request.json["value"]})
    response.raise_for_status()
    json = response.json()
    for record in json[request.json["value"]]:
        record_out_data = {
            "symbol": record.get("symbol"),
            "conid": record.get("conid"),
            "ccy_pair": record.get("ccyPair"),
        }
        record_out = api.core.Object(
            identifier=api.core.symbols.Identifier(record.get("symbol")),
            timestamp=api.core.symbols.Timestamp(),
            attribute=api.core.symbols.Attribute("currency_pair"),
            model=models_generated.CurrencyPair,
            _data=record_out_data,
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverExchangerateGetParametersQuery,
    returns=models.FXSpot,
    stores=tables.FXSpot,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_exchange_rate(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "exchangerate"
    response = await client.get(
        str(url), params={"source": request.json["source"], "target": request.json["target"]}
    )
    response.raise_for_status()
    json = response.json()
    record_out_data = {
        "base": request.json["source"],
        "terms": request.json["target"],
        "spot": json.get("rate"),
    }
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(
            ".".join([request.json["source"], request.json["target"]])
        ),
        timestamp=api.core.symbols.Timestamp(),
        attribute=api.core.symbols.Attribute("price"),
        model=models.FXSpot,
        _data=record_out_data,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.TrsrvAllConidsGetParametersQuery,
    returns=models_generated.TrsrvAllConidsGetResponse,
    requires={"client": api.core.deps.http.HttpClient},
)
async def trsrv_conids(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "trsrv" / "all-conids"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    for record in json["root"]:
        record_out = api.core.Object(
            identifier=api.core.symbols.Identifier(record.get("symbol")),
            timestamp=api.core.symbols.Timestamp(record.get("t")),
            attribute=api.core.symbols.Attribute("conid"),
            model=models_generated.TrsrvAllConidsGetResponseItem,
            _data=record,
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.TrsrvFuturesGetParametersQuery,
    returns=models.FuturesContract,
    stores=tables.FuturesChains,
    requires={"client": api.core.deps.http.HttpClient},
)
async def trsrv_futures_from_symbol(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "trsrv" / "futures"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    for symbol in json:
        for contract in json[symbol]:
            record_out = api.core.Object(
                identifier=api.core.symbols.Identifier(symbol),
                timestamp=api.core.symbols.Timestamp(contract.get("t")),
                attribute=api.core.symbols.Attribute("futures_contract"),
                model=models.FuturesContract,
                _data=contract,
            )
            yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.TrsrvSecdefScheduleGetParametersQuery,
    returns=models_generated.TradingScheduleItem,
    requires={"client": api.core.deps.http.HttpClient},
)
async def trsrv_schedule_from_symbol(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "trsrv" / "secdef" / "schedule"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    for record in json["root"]:
        yield api.core.Response(
            request=request,
            identifier=api.core.symbols.Identifier(record.get("symbol")),
            timestamp=api.core.symbols.Timestamp(record.get("t")),
            attribute=api.core.symbols.Attribute("schedule"),
            model=models_generated.TradingScheduleItem,
            _data=record,
        )


@api.core.router.define(
    accepts=models.ContractId,
    returns=models_generated.IserverContractConidInfoAndRulesGetResponse,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_contract_info_from_conid(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "contract" / request.json["root"] / "info-and-rules"
    response = await client.get(str(url))
    response.raise_for_status()
    json = response.json()
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(request.root),
        timestamp=None,
        attribute=api.core.symbols.Attribute("contract_info"),
        model=models_generated.IserverContractConidInfoAndRulesGetResponse,
        _data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverSecdefStrikesGetParametersQuery,
    returns=models.OptionsStrikes,
    stores=tables.OptionsStrikes,
)
async def iserver_strikes_from_conid(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "secdef" / "strikes"
    response = await client.get(url, params=request.json)
    response.raise_for_status()
    json = response.json()
    record_out_data = {
        "conid": request.json["conid"],
        "sectype": request.json["sectype"],
        "exchange": request.json["exchange"],
        "call": json["call"],
        "put": json["put"],
    }
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(request.json["conid"]),
        timestamp=None,
        attribute=api.core.symbols.Attribute("strikes"),
        model=models.OptionsStrikes,
        _data=record_out_data,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models_generated.IserverSecdefSearchGetParametersQuery,
    returns=models_generated.SecdefSearchResponse,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_secdef_search(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "secdef" / "search"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(request.json["conid"]),
        timestamp=None,
        attribute=api.core.symbols.Attribute("secdef_search"),
        model=models_generated.SecdefSearchResponse,
        _data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    returns=models_generated.GwApiV1AccountsGetResponse,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_accounts(client: AsyncClient) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "accounts"
    response = await client.get(str(url))
    response.raise_for_status()
    json = response.json()
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(json.get("root")),
        timestamp=None,
        attribute=api.core.symbols.Attribute("accounts"),
        model=models_generated.UserAccountsResponse,
        _data=json,
    )
    yield api.core.Response(None, record_out)


@api.core.router.define(
    accepts=models_generated.IserverSecdefInfoGetParametersQuery,
    returns=models_generated.SecDefInfoResponse,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_secdef_info(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "secdef" / "info"
    response = await client.get(str(url), params=request.json)
    response.raise_for_status()
    json = response.json()
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(request.json["conid"]),
        timestamp=None,
        attribute=api.core.symbols.Attribute("secdef_info"),
        model=models_generated.SecDefInfoResponse,
        _data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.OrderId,
    returns=models_generated.OrderStatus,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_account_order_status(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "account" / "order" / "status" / request.json["root"]
    response = await client.get(str(url))
    response.raise_for_status()
    json = response.json()
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(request.root),
        timestamp=None,
        attribute=api.core.symbols.Attribute("order_status"),
        model=models_generated.OrderStatus,
        _data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.OrderPayload,
    returns=models_generated.OrderSubmitSuccess
    | models_generated.OrderSubmitError
    | models_generated.OrderReplyMessage
    | models_generated.AdvancedOrderReject,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_account_post_order(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "iserver" / "account" / request.json["account_id"] / "orders"
    response = await client.post(url, json=request.json)
    response.raise_for_status()
    json = response.json()
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
        identifier=api.core.symbols.Identifier(request.json["account_id"]),
        timestamp=None,
        attribute=api.core.symbols.Attribute("order_submit"),
        model=model,
        _data=instance.model_dump(),
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.CancelOrder,
    returns=models_generated.OrderCancelSuccess | models_generated.OrderSubmitError,
    requires={"client": api.core.deps.http.HttpClient},
)
async def iserver_account_delete_order(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = (
        ROOT
        / "iserver"
        / "account"
        / request.json["account_id"]
        / "order"
        / request.json["order_id"]
    )
    response = await client.delete(url, verify=False)
    response.raise_for_status()
    json = response.json()
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
        identifier=api.core.symbols.Identifier(request.json["account_id"]),
        timestamp=None,
        attribute=api.core.symbols.Attribute("order_cancel"),
        model=model,
        _data=instance.model_dump(),
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    returns=models_generated.AccountAttributes,
    requires={"client": api.core.deps.http.HttpClient},
)
async def portfolio_accounts(client: AsyncClient) -> api.core.RouterReturnType:
    url = ROOT / "portfolio" / "accounts"
    response = await client.get(str(url))
    response.raise_for_status()
    json = response.json()
    for record in json["root"]:
        record_out = api.core.Object(
            identifier=api.core.symbols.Identifier(record.get("root")),
            timestamp=None,
            attribute=api.core.symbols.Attribute("account_attributes"),
            model=models_generated.AccountAttributes,
            _data=record,
        )
        yield api.core.Response(None, record_out)


@api.core.router.define(
    accepts=models.AccountId,
    returns=models.Ledger,
    stores=tables.AccountLedger,
    requires={"client": api.core.deps.http.HttpClient},
)
async def portfolio_account_ledger(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "portfolio" / request.json["root"] / "ledger"
    response = await client.get(str(url))
    response.raise_for_status()
    json = response.json()
    for currency, ledger in json["root"].items():
        record_out_data = {
            "currency": currency,
            **ledger,
        }
        record_out = api.core.Object(
            identifier=api.core.symbols.Identifier(request.json["root"]),
            timestamp=None,
            attribute=api.core.symbols.Attribute("account_ledger"),
            model=models.Ledger,
            _data=record_out_data,
        )
        yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.AccountId,
    returns=models_generated.PortfolioSummary,
    stores=tables.AccountSummary,
    requires={"client": api.core.deps.http.HttpClient},
)
async def portfolio_account_summary(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    url = ROOT / "portfolio" / request.json["root"] / "summary"
    response = await client.get(str(url), verify=False)
    response.raise_for_status()
    json = response.json()
    record_out = api.core.Object(
        identifier=api.core.symbols.Identifier(request.json["root"]),
        timestamp=None,
        attribute=api.core.symbols.Attribute("account_summary"),
        model=models_generated.PortfolioSummary,
        _data=json,
    )
    yield api.core.Response(request, record_out)


@api.core.router.define(
    accepts=models.AccountId,
    returns=models_generated.IndividualPosition,
    stores=tables.AccountPositions,
    requires={"client": api.core.deps.http.HttpClient},
)
async def portfolio_account_positions(client: AsyncClient, request: api.core.Request) -> api.core.RouterReturnType:
    page_id = 1
    while True:
        url = ROOT / "portfolio" / request.json["root"] / "positions" / page_id
        response = await client.get(str(url))
        response.raise_for_status()
        json = response.json()
        for record in json["root"]:
            record_out = api.core.Object(
                identifier=api.core.symbols.Identifier(request.json["root"]),
                timestamp=None,
                attribute=api.core.symbols.Attribute("account_positions"),
                model=models_generated.IndividualPosition,
                _data=record,
            )
            yield api.core.Response(request, record_out)
        if len(json["root"]) < 100:
            break
        page_id += 1
