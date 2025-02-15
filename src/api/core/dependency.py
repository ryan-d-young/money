from typing import AsyncContextManager, ClassVar, Protocol, TypeVar

DependencyT = TypeVar("DependencyT", bound=AsyncContextManager)


class Dependency[DependencyT](Protocol):
    name: ClassVar[str]
    exclusive: ClassVar[bool] = False
    _instance: ClassVar[DependencyT | None] = None

    async def start(self, env: dict[str, str]) -> None: ...
    async def __aenter__(self) -> DependencyT: ...
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...
    async def stop(self, env: dict[str, str]) -> None: ...

