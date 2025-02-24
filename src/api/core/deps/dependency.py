from asyncio import AbstractEventLoop
from contextvars import ContextVar
from typing import AsyncContextManager, ClassVar, Generic, Protocol, TypeVar

DependencyT = TypeVar("DependencyT", bound=AsyncContextManager)


class Dependency(Protocol, Generic[DependencyT]):
    name: ClassVar[str]
    core: ClassVar[bool] = False
    instance: ClassVar[DependencyT | None] = None

    @classmethod
    async def start(cls, env: dict[str, str], loop: AbstractEventLoop) -> None: ...
    async def __aenter__(self) -> DependencyT: ...
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...
    @classmethod
    async def stop(cls, env: dict[str, str]) -> None: ...


Dependencies = dict[str, Dependency]
DependencyDict = dict[str, ContextVar[DependencyT]]


