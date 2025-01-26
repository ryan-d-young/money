import pydantic

from . import models_generated


class AccountId(pydantic.RootModel[str]):
    root: str = pydantic.Field(...)


class OrderId(pydantic.RootModel[str]):
    root: str = pydantic.Field(...)


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
