from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from json import dumps
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from .request import Request, SerializableObj
from .symbols import Attribute, Identifier, Timestamp


@dataclass(frozen=True)
class Record(SerializableObj):
    identifier: Identifier | None = None
    timestamp: Timestamp | None = None
    attribute: Attribute | None = None
    _data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.identifier is None:
            raise ValueError("Identifier is required")

    @property
    def json(self) -> dict:
        record = {}
        for attr in ["identifier", "timestamp", "attribute"]:
            value = getattr(self, attr)
            if value is not None:
                record[attr] = value.json
        record.update(self._data)
        return record


@dataclass(frozen=True)
class Object(Record):
    model: type[BaseModel] | None = None

    def __post_init__(self):
        super().__post_init__()
        if self.model is None:
            raise ValueError("Model is required")

    @property
    def json(self) -> dict:
        model_instance = self.model(**self._data)
        data = model_instance.model_dump(exclude_none=True)
        for attr in ["identifier", "timestamp", "attribute"]:
            value = getattr(self, attr)
            if value is not None:
                data[attr] = value.json
        return data


@dataclass(frozen=True)
class Response(SerializableObj):
    request: Request
    _data: Object | Record

    def __repr__(self):
        return f"<Response({self.id})>"

    @property
    def id(self) -> UUID:
        return self.request.id

    @property
    def json(self) -> dict:
        return self._data.json

    @property
    def model(self) -> type[BaseModel] | None:
        if isinstance(self._data, Object):
            return self._data.model
        raise ValueError("Response data is not an Object")


ResponseFactory = AsyncGenerator[Response, None]
