from datetime import datetime

import pydantic

from . import models_generated


class AccountId(pydantic.RootModel[str]):
    root: str = pydantic.Field(...)


class OrderId(pydantic.RootModel[str]):
    root: str = pydantic.Field(...)


class ContractId(pydantic.RootModel[int]):
    root: int = pydantic.Field(...)


class Order(pydantic.BaseModel):
    account_id: AccountId = pydantic.Field(...)
    order_id: OrderId = pydantic.Field(...)


class Ledger(models_generated.Ledger1):
    currency: str = pydantic.Field(...)


class OrderPayload(models_generated.Order):
    account_id: str = pydantic.Field(exclude=True)


class CancelOrder(pydantic.BaseModel):
    account_id: str = pydantic.Field(...)
    order_id: str = pydantic.Field(...)


class FXSpot(pydantic.BaseModel):
    base: models_generated.Currency = pydantic.Field(...)
    terms: models_generated.Currency = pydantic.Field(...)
    spot: float = pydantic.Field(...)


class FuturesContract(pydantic.BaseModel):
    symbol: str = pydantic.Field(...)
    conid: int = pydantic.Field(...)
    underlying_conid: int = pydantic.Field(alias="underlyingConid")
    expiration_date: int = pydantic.Field(alias="expirationDate")
    ltd: int = pydantic.Field(...)
    short_cutoff: int = pydantic.Field(alias="shortFuturesCutOff")
    long_cutoff: int = pydantic.Field(alias="longFuturesCutOff")

    class Config:
        allow_population_by_field_name = True

    @pydantic.field_validator("expiration_date", "ltd", "short_cutoff", "long_cutoff", mode="before")
    def validate_dt(self, value: int) -> datetime:
        return datetime.strptime(str(value), "%Y%m%d")


class FuturesChain(pydantic.BaseModel):
    contracts: dict[str, list[FuturesContract]] = pydantic.Field(...)


class OptionsStrikes(pydantic.BaseModel):
    conid: int = pydantic.Field(...)
    sectype: str = pydantic.Field(...)
    exchange: str = pydantic.Field(...)
    call: list[int] = pydantic.Field(...)
    put: list[int] = pydantic.Field(...)
    