from datetime import datetime

import pydantic
import sqlmodel

from .symbols import Identifier, Timestamp


class Request(pydantic.BaseModel):
    source: str = pydantic.Field(...)
    router: str = pydantic.Field(...)


class Record(sqlmodel.SQLModel):
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    timestamp: Timestamp = sqlmodel.Field(
        default_factory=lambda _: datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    )
    identifier: Identifier = sqlmodel.Field(...)


class Object(Record):
    obj: pydantic.BaseModel = sqlmodel.Field(default=None)


class Response(pydantic.BaseModel):
    request: Request = pydantic.Field(...)
    data: list[Record] | list[Object] = pydantic.Field(...)
    