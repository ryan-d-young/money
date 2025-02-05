from functools import wraps
from typing import Callable, Union, AsyncGenerator, TypedDict, Unpack

import pydantic
from sqlalchemy import Table

from .core import protocols


class Info(TypedDict, total=False):
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
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    stores: Table | None
    requires: list[protocols.Dependency] | None


def define(**info: Unpack[Info]) -> Callable[[protocols.Router], protocols.Router]:
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
        wrapped.info = Info(**info)
        return wrapped
    return decorator
