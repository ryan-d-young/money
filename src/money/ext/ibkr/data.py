from typing import Generator

from src.money import core
from src.money.deps import http
from . import models

import yarl
import pydantic
import sqlmodel


ROOT = yarl.URL("https://api.ibkr.com/v1/api/").build()



class HmdsHistoricalRequest(http.HTTPRequest):
    url = ROOT / "hmds" / "history"
    method = "get"
    params: models.HmdsHistoryGetParametersQuery = pydantic.Field(...)


class IserverHistoricalRequest(http.HTTPRequest):
    url = ROOT / "iserver" / "marketdata" / "history"
    method = "get"
    params: models.IserverMarketdataHistoryGetParametersQuery = pydantic.Field(...)


class BarRecord(core.Record, Table=True):
    __tablename__ = "bar"
    o: float | None = sqlmodel.Column("open")
    h: float | None = sqlmodel.Column("high")
    l: float | None = sqlmodel.Column("low")
    c: float | None = sqlmodel.Column("close")


def store_historical_bar_response(
    request: HmdsHistoricalRequest | IserverHistoricalRequest, 
    response: models.HmdsHistoryResponse | models.IserverHistoryResponse
) -> Generator[BarRecord, None]:
    identifier = request.params.conid
    for bar in response.data:
        yield BarRecord(
            identifier=identifier, 
            timestamp=bar.t, 
            o=bar.o, h=bar.h, l=bar.l, c=bar.c
        )
