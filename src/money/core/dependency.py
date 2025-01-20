from typing import Any, Protocol, AsyncContextManager, ClassVar, Any


class Dependency[AsyncContextManager](Protocol):
    name: ClassVar[str]
    started: bool = False
    _obj: Any = None
    async def start(self) -> None:
        ...

    async def __aenter__(self) -> Any:
        ...

    async def __aexit__(self, exc_t, exc_v, exc_tb) -> None:
        ...

    async def stop(self) -> None:
        ...
