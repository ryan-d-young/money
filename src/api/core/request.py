import asyncio
from typing import TypeVar, Unpack

from pydantic import BaseModel

from src.util import dt, ident

RequestModelT = TypeVar("RequestModelT", bound=type[BaseModel])
RequestInstanceT = TypeVar("RequestInstanceT", bound=BaseModel)


class Request[RequestModelT, RequestInstanceT]:
    _id: ident.UUID
    _created_at: float
    _completed_at: float | None
    _data: RequestInstanceT | None
    _model: RequestModelT

    def __init__(self, model: RequestModelT):
        self._model = model
        self._data = None
        self._id = ident.uuid()
        self._created_at = dt.now()
        self._completed_at = None
        self._lock = asyncio.Lock()

    def __repr__(self):
        s = f"{self._model.__name__}({self._id})"
        if self.completed:
            return f"{s}:\n {self.data}"
        return s

    @property
    def id(self):
        return self._id

    @property
    def data(self):
        return self._data

    @property
    def completed(self) -> bool:
        return self._completed_at is not None

    @property
    def elapsed(self) -> float | None:
        if self.completed:
            return self._completed_at - self._created_at

    async def make(self, **kwargs: Unpack[RequestModelT]) -> None:
        if self.completed:
            raise ValueError(f"An instance of {self} already exists")
        async with self._lock:
            self._data = self._model(**kwargs)
            self._completed_at = dt.now()
