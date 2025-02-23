from dataclasses import dataclass, field
from typing import AsyncGenerator

from pydantic import BaseModel

from .request import Request
from .symbols import Attribute, Identifier, Serializable, Timestamp


@dataclass(frozen=True)
class Record:
    identifier: Identifier | None = None
    timestamp: Timestamp | None = None
    attribute: Attribute | None = None
    _data: Serializable = field(default_factory=dict)

    def __post_init__(self):
        if self.identifier is None:
            raise ValueError("Identifier is required")

    @property
    def data(self) -> dict:
        return {
            "identifier": self.identifier.json,
            "timestamp": self.timestamp.json,
            "attribute": self.attribute.json,
            **self._data,
        }


@dataclass(frozen=True)
class Object(Record):
    model: type[BaseModel] = field(default_factory=BaseModel)

    @property
    def data(self) -> dict:
        model_instance = self.model(**self._data)
        data = model_instance.model_dump(exclude_none=True)
        return {
            "identifier": self.identifier.json,
            "timestamp": self.timestamp.json,
            "attribute": self.attribute.json,
            **data,
        }


@dataclass(frozen=True)
class Response(Serializable):
    request: Request | None = None
    _data: Object | Record | None = field(default_factory=Record)

    def __repr__(self):
        return f"<Response({self.id})>"

    @property
    def id(self) -> str:
        return self.request.id
    
    @property
    def json(self) -> dict:
        return self._data.data

    @property
    def model(self) -> type[BaseModel] | None:
        if isinstance(self._data, Object):
            return self._data.model
        raise ValueError("Response data is not an Object")


ResponseFactory = AsyncGenerator[Response, None]
