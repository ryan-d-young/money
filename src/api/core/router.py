import functools
from dataclasses import dataclass
from typing import Callable, Union, AsyncGenerator, TypedDict, Unpack, ClassVar, TypeVar

import pydantic
from sqlalchemy import Table

from src.util import dt
from .dependency import Dependencies
from .request import Request
from .response import Response

RateLimitT = TypeVar("RateLimitT", bound=tuple[int, float])  # (limit, seconds)


@dataclass(slots=True)
class Metadata:
    history: dict[dt.datetime, Request] = None
    rate_limit: RateLimitT | None = None

    def __post_init__(self):
        self.history = {}


class Info(TypedDict, total=False):
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    stores: Table | None
    requires: Dependencies | None


class Router(Callable[[Request, Dependencies], AsyncGenerator[Response, None]]):
    metadata: ClassVar[Metadata]
    info: ClassVar[Info]

    async def __call__(
        self,
        request: Request,
        **dependencies: Dependencies,
    ) -> AsyncGenerator[Response, None]: ...


def define(**info: Unpack[Info]) -> Callable[[Router], Router]:
    """
    A decorator to define a router function. Attaches 'Info' and 'Context' to the router function.

    Parameters:
        accepts (type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None):
            The type of data model that the API route accepts.
        returns (type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None):
            The type of data model that the API route returns.
        stores (Table | None):
            The database table where the data is stored.
        requires (list[protocols.Dependency] | None):
            A list of dependencies required by the API route.
        rate_limit (RateLimit | None):
            The external rate limit, in (limit, seconds).

    Returns:
    Callable[[protocols.Router], protocols.Router]:
        A decorated router function with attached 'Info' and 'Context'.
    """

    def decorator(router: Router) -> Router:
        @functools.wraps(router)
        def wrapper(request: Request, **dependencies: Unpack[Dependencies]):
            # dependencies injected from Session.__call__
            # store request in history before passing to router
            wrapper.metadata.history[dt.now()] = request
            return router(request=request, **dependencies)
        # attach metadata and info to wrapper
        wrapper.metadata = Metadata()
        wrapper.info = Info(**info)
        return wrapper
    # decorated function processes request and contains metadata/info
    return decorator
