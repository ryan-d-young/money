from typing import TypeVar, TypedDict, Protocol, Unpack

from pydantic import BaseModel

from src.util import dt, ident
from .symbols import Identifier, Attribute, Timestamp

RequestModelT = TypeVar("RequestModelT", bound=type[BaseModel])
RequestInstanceT = TypeVar("RequestInstanceT", bound=BaseModel)


class Serializable(Protocol):
    def data(self) -> dict:
        ...


class RequestKwargs(TypedDict, total=False):
    identifier: Identifier
    attribute: Attribute | None
    timestamp: Timestamp | None


class Request[RequestInstanceT]:
    _id: ident.UUID
    _submitted_at: float
    _created_at: float | None
    _data: RequestInstanceT | None
    _model: RequestModelT

    def __init__(self, model: RequestModelT):
        self._model = model
        self._data = None
        self._id = ident.uuid()
        self._submitted_at = dt.now()

    def __repr__(self):
        s = f"{self._model.__name__}({self._id})"
        if self._created_at:
            return f"{s}:\n {self.data}"
        return s

    @property
    def id(self):
        return self._id

    def make(self, **kwargs: RequestKwargs | Unpack[RequestModelT]) -> Serializable:
        if self._data:
            raise ValueError(f"An instance of {self} already exists")
        self._data = self._model(**kwargs)
        self._created_at = dt.now()
        return self._data

    @property
    def data(self) -> Serializable:
        if not self._data:
            raise ValueError(f"{self} is not set")
        return self._data.model_dump(exclude_none=True)
