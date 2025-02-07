from importlib import import_module
from pathlib import Path
from functools import wraps
from typing import Callable, Union, AsyncGenerator, TypedDict, Unpack, ClassVar, Protocol
from types import ModuleType

import pydantic
from sqlalchemy import Table

from .core import dependency


class Info(TypedDict, total=False):
    accepts: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    returns: type[pydantic.BaseModel] | Union[type[pydantic.BaseModel]] | None
    stores: Table | None
    requires: list[dependency.Dependency] | None


class Router(Protocol):
    def __call__(
        self, 
        request: pydantic.BaseModel | None = None, 
        **args: dict[str, dependency.Dependency]
    ) -> AsyncGenerator[dict, None]:
        ...
        

def define(**info: Unpack[Info]) -> Callable[[dependency.Router], dependency.Router]:
    """
    A decorator to define metadata for a router function. Attaches 'Info' to the router function.

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
        A decorated router function with attached 'Info'.
    """
    def decorator(router: dependency.Router) -> dependency.Router:
        @wraps(router)
        async def wrapped(**kwargs) -> AsyncGenerator[dict, None]:
            return router(**kwargs)
        wrapped.info = Info(**info)
        return wrapped
    return decorator


class Registry:
    data: ClassVar[dict[str, dict[str, dependency.Router]]] = {}

    @classmethod
    def scan(cls, ext_root: Path):
        for fp in ext_root.walk():
            if fp.stem == "routers":
                routers: ModuleType = import_module(".".join("src", "ext", fp.parent, fp.stem))
                for fname, fn in routers.__dict__.items():
                    if isinstance(fn, dependency.Router):
                        if hasattr(fn, "info"):
                            cls.data[fp.parent][fname] = fn
