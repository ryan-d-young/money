from typing import Any, NotRequired, TypedDict
from uuid import UUID

from pydantic import BaseModel

from src import util

from .symbols import Attribute, Identifier, Serializable, Timestamp

RequestModel = type[BaseModel]


class SerializableObj(Serializable):
    @property
    def json(self) -> dict: ...


class _RequestKwargs(TypedDict, total=False):
    identifier: Identifier
    attribute: NotRequired[Attribute]
    timestamp: NotRequired[Timestamp]


RequestKwargs = _RequestKwargs | dict[str, Any]


class Request(SerializableObj):
    _id: UUID
    _submitted_at: util.dt.datetime

    def __init__(self, model: RequestModel | None = None):
        self._model = model
        self._data = None
        self._id = util.ident.uuid()
        self._submitted_at = util.dt.now()

    def __repr__(self):
        return f"<Request({self._id})>"

    @property
    def data(self) -> dict | None:
        if not self._data:
            return None
        return dict(self._data)

    @property
    def model(self) -> RequestModel | None:
        return self._model

    @property
    def id(self) -> UUID:
        return self._id

    def make(self, **kwargs: RequestKwargs) -> None:
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
        return self._data

    def __getitem__(self, key: str) -> Any:
        return self.json[key]
