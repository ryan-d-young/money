from typing import TypedDict
from dataclasses import dataclass

from pydantic import BaseModel

from .request import Request, Serializable
from .symbols import Attribute, Identifier, Timestamp


def empty() -> dict[str, dict[str, None]]:
    return {"data": dict()}


class Record(TypedDict, total=False):
    identifier: Identifier
    timestamp: Timestamp | None
    attribute: Attribute | None
    _data: Serializable

    @property
    def data(self) -> dict:
        return {
            "identifier": self["identifier"].obj,
            "timestamp": self["timestamp"].obj,
            "attribute": self["attribute"].obj,
            **self["_data"],
        }


class Object(Record):
    model: type[BaseModel]

    @property
    def data(self) -> dict:
        model_instance = self.model(**self["_data"])
        data = model_instance.model_dump(exclude_none=True)
        return {
            "identifier": self["identifier"].obj,
            "timestamp": self["timestamp"].obj,
            "attribute": self["attribute"].obj,
            **data,
        }


@dataclass(frozen=True)
class Response(Serializable):
    request: Request
    _data: Object | Record | None = None

    def __post_init__(self):
        self._data = self._data or empty()

    def __repr__(self):
        return f"<Response({self.id})>"

    @property
    def id(self) -> str:
        return self.request.id
    
    @property
    def data(self) -> dict:
        return self._data.data

    @property
    def model(self) -> type[BaseModel] | None:
        return getattr(self._data, "model", None)
