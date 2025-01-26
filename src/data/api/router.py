from dataclasses import dataclass, field
from functools import wraps
from typing import TypeVar, Callable, Union

import pydantic
from sqlalchemy import Table

from .core import protocols

RouterT = TypeVar("RouterT", bound=Callable[[data.Request], data.Response])


@dataclass(frozen=True)
class Info:
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None = None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None = None
    stores: Table | None = None
    requires: list[protocols.Dependency] | None = field(default_factory=list)


def define(
    *,
    accepts: type[pydantic.BaseModel] | None = None,
    returns: type[pydantic.BaseModel] | None = None,
    stores: Table | None = None, 
    requires: list[protocols.Dependency] | None = None,
) -> Callable[[RouterT], RouterT]:
    def decorator(f: RouterT) -> RouterT:
        @wraps(f)
        def wrapped(*args, **kwargs):
            model_instance = accepts(**kwargs)
            return f(*args, model_instance)
        wrapped.info = Info(accepts, returns, stores, requires)
        return wrapped
    return decorator
