from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, Union, AsyncGenerator

import pydantic
from sqlalchemy import Table

from .core import protocols


@dataclass(frozen=True)
class Info:
    """
    A class to represent the metadata for API routes.

    Attributes:
        accepts (type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None): 
            The type of data model that the API route accepts.
        returns (type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None): 
            The type of data model that the API route returns.
        stores (Table | None): 
            The database table where the data is stored.
        requires (list[protocols.Dependency] | None): 
            A list of dependencies required by the API route.
    """
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None = None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None = None
    stores: Table | None = None
    requires: list[protocols.Dependency] | None = field(default_factory=list)


def define(
    *,
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None = None,
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None = None,
    stores: Table | None = None,
    requires: list[protocols.Dependency] | None = None,
) -> Callable[[protocols.Router], protocols.Router]:
    """
    A decorator to define metadata for a router function. Attaches 'Info' to the router function.

    Parameters:
        See `Info` class attributes.

    Returns:
    Callable[[protocols.Router], protocols.Router]: 
        A decorated router function with attached 'Info'.
    """
    def decorator(router: protocols.Router) -> protocols.Router:
        @wraps(router)
        async def wrapped(**kwargs) -> AsyncGenerator[dict, None]:
            return router(**kwargs)
        wrapped.info = Info(accepts, returns, stores, requires)
        return wrapped
    return decorator
