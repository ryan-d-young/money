from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from functools import partial
from typing import Callable, TypedDict, Unpack, Protocol, TypeVar

import pydantic
from sqlalchemy import Table

from src.util import dt

from .deps import Dependencies
from .request import Request
from .response import Response

RateLimit = tuple[int, float]  # (limit, seconds)
RouterReturnType = AsyncGenerator[Response, None]
BoundRouterReturnType = partial[RouterReturnType]


@dataclass(slots=True)
class Metadata:
    history: dict[float, Request] = field(default_factory=dict)
    rate_limit: RateLimit | None = None

    def __post_init__(self):
        self.history = {}


class Info(TypedDict, total=False):
    accepts: type[pydantic.BaseModel] | None
    returns: type[pydantic.BaseModel] | None
    stores: Table | None
    requires: Dependencies | None


RouterT = TypeVar("RouterT", bound=Callable[..., RouterReturnType])


class Router(Protocol):
    info: Info
    metadata: Metadata
    async def __call__(
        self,
        request: Request,
        **dependencies: Dependencies,
    ) -> AsyncGenerator[Response, None]: ...


class WrappedRouter:
    def __init__(self, router: RouterT, info: Info):
        self.router = router
        self.info = info
        self.metadata = Metadata()

    async def __call__(self, request: Request, **dependencies: Dependencies) -> AsyncGenerator[Response, None]:
        now = dt.utcnow()
        self.metadata.history[now] = request
        async for response in self.router(request, **dependencies):
            yield response


def define(**info: Unpack[Info]) -> Callable[[RouterT], Router]:
    """Define a router function. Attaches 'Info' and 'Metadata' to the router function.

    Parameters
    ----------
        accepts (type[pydantic.BaseModel] | None):
            The type of data model that the API route accepts.
        returns (type[pydantic.BaseModel] | None):
            The type of data model that the API route returns.
        stores (Table | None):
            The database table where the data is stored.
        requires (list[protocols.Dependency] | None):
            A list of dependencies required by the API route.
        rate_limit (RateLimit | None):
            The external rate limit, in (limit, seconds).

    Returns
    -------
        Callable[[RouterT], Router]:
            A decorated router function with attached 'Info' and 'Metadata'.
    """

    def decorator(router: RouterT) -> Router:
        return WrappedRouter(router, info)
    return decorator
