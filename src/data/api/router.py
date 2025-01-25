from dataclasses import dataclass, field
from functools import wraps
from typing import TypeVar, Callable

from sqlalchemy import Table

from .core import data, protocols

RouterT = TypeVar("RouterT", bound=Callable[[data.Request], data.Response])


@dataclass(frozen=True)
class info:
    accepts: type[data.Request]
    returns: type[data.Response]
    stores: Table
    requires: list[protocols.Dependency] | None = field(default_factory=list)


def define(
    *,
    accepts: type[data.Request], 
    returns: type[data.Response], 
    stores: Table, 
    requires: list[protocols.Dependency] | None = None,
) -> Callable[[RouterT], RouterT]:
    def decorator(f: RouterT) -> RouterT:
        @wraps(f)
        def wrapped(*args, **kwargs):
            return f(*args, **kwargs)
        wrapped.info = info(accepts, returns, stores, requires)
        return wrapped
    return decorator
