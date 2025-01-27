from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, Union, Any, AsyncGenerator

import pydantic
from sqlalchemy import Table

from .core import protocols


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
) -> Callable[[protocols.Router], protocols.Router]:
    def decorator(router: protocols.Router) -> protocols.Router:
        @wraps(router)
        async def wrapped(**kwargs) -> AsyncGenerator[dict, None]:
            return router(**kwargs)
        wrapped.info = Info(accepts, returns, stores, requires)
        return wrapped
    return decorator
