from typing import Protocol, AsyncContextManager


class Dependency(Protocol):
    _instance: AsyncContextManager | None = None
    async def start(self, env: dict[str, str]) -> None: ...
    async def stop(self, env: dict[str, str]) -> None: ...
