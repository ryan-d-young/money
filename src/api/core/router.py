import functools
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Callable, ClassVar, TypedDict, Unpack

import pydantic
from sqlalchemy import Table

from src.util import dt

from .deps import Dependencies
from .request import Request
from .response import Response

RateLimit = tuple[int, float]  # (limit, seconds)
RouterReturnType = AsyncGenerator[Response, None]


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


class Router(type[Callable[[Request, Dependencies], RouterReturnType]]):
    metadata: ClassVar[Metadata]
    info: ClassVar[Info]

    async def __call__(
        self,
        request: Request,
        **dependencies: Dependencies,
    ) -> RouterReturnType: ...


def define(**info: Unpack[Info]) -> Callable[[Router], Router]:
    """Define a router function. Attaches 'Info' and 'Context' to the router function.

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
        Callable[[Router], Router]:
            A decorated router function with attached 'Info' and 'Context'.

    """

    def decorator(router: Router) -> Router:
        @functools.wraps(router)
        def wrapper(request: Request, **dependencies: Dependencies) -> AsyncGenerator[Response, None]:
            # dependencies injected from Session.__call__
            # store request in history before passing to router
            now = dt.now()
            wrapper.metadata.history[now] = request
            return router(request=request, **dependencies)

        # attach metadata and info to wrapper
        wrapper.metadata = Metadata()
        wrapper.info = Info(**info)
        return wrapper

    # decorated function processes request and contains metadata/info
    return decorator
