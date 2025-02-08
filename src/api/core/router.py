import functools
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Callable, Union, AsyncGenerator, TypedDict, Unpack, ClassVar, Protocol, Awaitable
from logging import Logger

import pydantic
from sqlalchemy import Table

from src import util
from . import dependency, request, response


class RateLimit(TypedDict):
    """
    A rate limit for a router.

    Attributes:
        limit (int): The maximum number of requests per period.
        period (int): The period in **seconds**.
    """
    limit: int
    period: int


class Metadata(TypedDict, total=False):
    rate_limit: RateLimit | None


class Info(TypedDict, total=False):
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    stores: Table | None
    requires: list[dependency.Dependency] | None


@dataclass(slots=True)
class Context:
    logger: Logger
    history: list[request.Request] | None = None
    metadata: Metadata | None = None

    def __post_init__(self):
        self.history = []
        self.metadata = {}

    def clear(self):
        self.history = []


class Router(Protocol):
    def __call__(
        self, 
        request: request.Request | None = None, 
        **args: dict[str, dependency.Dependency]
    ) -> AsyncGenerator[response.Response, None]:
        ...


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

    Returns:
    Callable[[protocols.Router], protocols.Router]: 
        A decorated router function with attached 'Info' and 'Context'.
    """
    def decorator(router: Router) -> Router:
        @functools.wraps(router)
        def wrapper(*args, **kwargs):
            return router(*args, **kwargs)
        wrapper.info = Info(**info)
        logger = util.log.get_logger(__name__)
        wrapper.context = Context(logger=logger)
        return wrapper
    return decorator


def metadata(**metadata: Unpack[Metadata]) -> Callable[[Router], Router]:
    """
    A decorator to define metadata for a router function. Attaches 'Metadata' to the router function's 'Context'.
    This decorator must be used after the 'define' decorator, as 'Context' is attached to the router function by 
    the 'define' decorator.

    Parameters:
        rate_limit (RateLimit | None): 
            The rate limit for the router.
    """
    def decorator(router: Router) -> Router:
        @functools.wraps(router)
        def wrapper(*args, **kwargs):
            return router(*args, **kwargs)
        wrapper.context.metadata.update(metadata)
        return wrapper
    return decorator


class Registry:
    data: ClassVar[dict[str, dict[str, Router]]] = {}
    _logger: Logger

    @classmethod
    def scan(cls, ext_root: Path, logger: Logger):
        cls._logger = logger
        for fp in ext_root.walk():
            if fp.stem == "routers":
                cls._logger.info(f"Scanning provider {fp.parent}")
                routers = import_module(".".join("src", "ext", fp.parent, fp.stem))
                for fname, fn in routers.__dict__.items():
                    if hasattr(fn, "info") and hasattr(fn, "context"):
                        cls._logger.info(f"Found router {fname}")
                        cls.data[fp.parent][fname] = fn
        return cls

    @classmethod
    def get(cls, provider: str, router: str) -> Router:
        cls._logger.info(f"Router {router} from {provider} accessed")
        return cls.data[provider][router]

    @classmethod
    def call(
        cls, 
        provider: str, 
        router: str, 
        request: request.Request, 
        **kwargs: dict[str, dependency.Dependency]
    ) -> Awaitable[response.Response]:
        router = cls.get(provider, router)
        coro = router(request, **kwargs)
        return coro
    