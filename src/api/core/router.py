import functools
from dataclasses import dataclass
from typing import (
    Callable,
    Union,
    AsyncGenerator,
    TypedDict,
    Unpack,
    Protocol,
)

import pydantic
from sqlalchemy import Table

from .dependency import Dependencies
from .request import Request
from .response import Response


RateLimit = tuple[int, float]  # (limit, seconds)


@dataclass(slots=True)
class Metadata:
    history: list[Request] | None = None
    def __post_init__(self):
        self.history = []


class Info(TypedDict, total=False):
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    stores: Table | None
    requires: Dependencies | None
    rate_limit: RateLimit | None = None


class Router(Protocol):
    metadata: Metadata
    info: Info
    async def __call__(
        self,
        request: Request | None = None,
        **kwargs: Dependencies,
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
        def wrapper(*args, **kwargs):
            return router(*args, **kwargs)

        wrapper.metadata = Metadata()
        wrapper.info = Info(**info)
        return wrapper

    return decorator
