from asyncio.tasks import Task, create_task
from functools import wraps
from typing import TypeVar, Callable, Awaitable, Any, Protocol, Unpack

import pydantic

from .dependency import Dependency
from .data import Request, Response


RouterT = TypeVar("RouterT", bound=Callable[[tuple[Dependency], Unpack[dict[str, Any]]], Response])
StorageT = TypeVar("StorageT", bound=Callable[[Response], None])


class Callback(Protocol):
    def __call__(self, fname: str, *deps: Dependency, **kwargs) -> None:
        ...


class RouterMetadata(pydantic.BaseModel):
    pass


class Router:
    def __init__(
        self, 
        f: RouterT,
        accepts: Request | None = None,
        returns: Response | None = None,
        storage: StorageT | None = None,
        depends_on: list[Dependency] | None = None,
        calls_back: list[Callback] | None = None,
        metadata_cls: type[RouterMetadata] | None = None
    ):
        self.f = f
        self.accepts = accepts
        self.returns = returns
        self.storage = storage or (lambda resp: resp)
        self.depends_on = depends_on or []
        self.calls_back = calls_back or []
        self.metadata_cls = metadata_cls

    def register_callback(self, callback: Callback) -> None:
        self.calls_back.append(callback)

    @property
    def name(self):
        return self.f.__name__

    def __call__(self, **kwargs) -> Task:
        if self.accepts is not None:
            model_inst = self.accepts(**kwargs)
            kwargs = model_inst.model_dump()
        elif kwargs:
            raise ValueError("Router does not accept kwargs")
        for callback in self.calls_back:
            callback(self.f.__name__, **kwargs)
        coro = self.f(*self.depends_on, **kwargs)
        task = create_task(coro)
        return task


def route(
    router, 
    accepts: Request | None = None,
    returns: Response | None = None,
    storage: StorageT | None = None,
    depends_on: list[Dependency] | None = None,
    calls_back: list[Callback] | None = None
) -> Router:
    @wraps(router)
    async def wrapped(*args, **kwargs):
        return router(*args, **kwargs)
    return Router(wrapped, accepts, returns, storage, depends_on, calls_back)
