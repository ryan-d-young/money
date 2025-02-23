from typing import TypeVar, TypedDict, Unpack, Any

from pydantic import BaseModel

from src.util import dt, ident
from .symbols import Serializable, Identifier, Attribute, Timestamp

RequestModelT = TypeVar("RequestModelT", bound=type[BaseModel])
RequestInstanceT = TypeVar("RequestInstanceT", bound=BaseModel)


class RequestKwargs(TypedDict, total=False):
    identifier: Identifier
    attribute: Attribute | None
    timestamp: Timestamp | None


class Request[RequestInstanceT](Serializable):
    _id: ident.UUID
    _submitted_at: float
    _created_at: float | None
    _data: dict | None
    _model: RequestModelT | None

    def __init__(self, model: RequestModelT | None = None):
        self._model = model
        self._data = None
        self._id = ident.uuid()
        self._submitted_at = dt.now()

    def __repr__(self):
        return f"<Request({self._id})>"

    @property
    def id(self):
        return self._id

    def make(self, **kwargs: RequestKwargs | Unpack[RequestModelT]) -> Serializable:
        if self._data:
            raise ValueError(f"An instance of {self} already exists")
        if self._model:
            self._data = self._model(**kwargs).model_dump(exclude_none=True)
        else:
            self._data = kwargs

    @property
    def json(self) -> dict:
        if not self._data:
            raise ValueError(f"{self} is not set")
        return dict(self._data)

    def __getitem__(self, key: str) -> Any:
        return self.json[key]
