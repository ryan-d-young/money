from dataclasses import dataclass

from pydantic import BaseModel

from .request import Request, Serializable
from .symbols import Attribute, Identifier, Timestamp


@dataclass(frozen=True)
class Record:
    identifier: Identifier
    timestamp: Timestamp | None = None
    attribute: Attribute | None = None
    _data: Serializable = None

    def __post_init__(self):
        self.data = self.data or dict()

    @property
    def data(self) -> dict:
        return {
            "identifier": self.identifier.obj,
            "timestamp": self.timestamp.obj,
            "attribute": self.attribute.obj,
            **self._data,
        }


@dataclass(frozen=True)
class Object(Record):
    model: type[BaseModel]

    @property
    def data(self) -> dict:
        model_instance = self.model(**self._data)
        data = model_instance.model_dump(exclude_none=True)
        return {
            "identifier": self.identifier.obj,
            "timestamp": self.timestamp.obj,
            "attribute": self.attribute.obj,
            **data,
        }


@dataclass(frozen=True)
class Response(Serializable):
    request: Request | None = None
    _data: Object | Record | None = None

    def __post_init__(self):
        self._data = self._data or Record(
            timestamp=Timestamp(),
            _data=dict(),
        )

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
        if isinstance(self._data, Object):
            return self._data.model
        raise ValueError("Response data is not an Object")
