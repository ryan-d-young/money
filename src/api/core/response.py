from typing import TypedDict

from pydantic import BaseModel

from .request import Request, Serializable
from .symbols import Attribute, Identifier, Timestamp


def empty() -> dict[str, dict[str, None]]:
    return {"data": dict()}


class Record(TypedDict, total=False):
    identifier: Identifier
    timestamp: Timestamp | None
    attribute: Attribute | None
    data: Serializable


class Object(Record):
    model: type[BaseModel]

    def __post_init__(self):
        data = self.model(**self.data)
        self["data"] = data.model_dump()


class Response(Serializable):
    def __init__(self, request: Request, data: Object | Record | None = None):
        self.request = request
        self._data = data or empty()

    def __post_init__(self):
        if not isinstance(self.data, (Object, Record)):
            raise ValueError("data must be an Object or Record")
        if not self.timestamp:
            self.timestamp = Timestamp()

    @property
    def data(self) -> dict:
        return {
            "timestamp": self._data["timestamp"],
            "identifier": self._data["identifier"],
            "attribute": self._data["attribute"],
            **self._data["data"],
        }

    def __repr__(self):
        return f"<Response({self.request})>"

    @property
    def id(self) -> str:
        return self.request.id
    