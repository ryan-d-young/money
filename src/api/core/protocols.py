from abc import ABC, abstractmethod
from typing import Protocol, AsyncContextManager, TypeVar, Any, Coroutine, AsyncGenerator

from pydantic import BaseModel


DependencyT = TypeVar("DependencyT", bound=AsyncContextManager)
ReturnType = TypeVar("ReturnType", bound=dict)


class Dependency[DependencyT](Protocol):
    async def start(self, env: dict[str, str]) -> None: ...
    async def __aenter__(self): ...
    async def __aexit__(self): ...
    async def stop(self, env: dict[str, str]) -> None: ...


class BaseDependency(Dependency, ABC):
    _instance: DependencyT | None = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self._instance.__class__.__name__})"

    @classmethod
    @abstractmethod
    async def start(cls, env: dict[str, str]) -> None:
        raise NotImplementedError(f"{cls} start method not implemented")

    @classmethod
    async def __aenter__(cls) -> Any:
        if cls._instance is None:
            raise RuntimeError(f"Dependency {cls} is not started")
        return cls._instance

    @classmethod
    async def __aexit__(cls, exc_type, exc_val, exc_tb) -> None:
        return

    @classmethod
    @abstractmethod
    async def stop(cls, env: dict[str, str]) -> None:
        raise NotImplementedError(f"{cls} stop method not implemented")


class Router(Protocol):
    def __call__(
        self, 
        request: BaseModel | None = None, 
        **kwargs: dict[str, Dependency]
    ) -> AsyncGenerator[dict, None]:
        ...
        