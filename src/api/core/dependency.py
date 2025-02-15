import asyncio
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


Dependencies = dict[str, Dependency]
Locks = dict[str, asyncio.Lock | None]

class DependencyManager:
    dependencies: Dependencies
    locks: Locks

    def __init__(self, *dependencies: Dependency):
        dependencies, locks = {}, {}
        for dependency in dependencies:
            dependencies[dependency.name] = dependency
            locks[dependency.name] = asyncio.Lock() if dependency.exclusive else None
        self.dependencies, self.locks = dependencies, locks

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dependencies})"

    async def get(self, name: str) -> Dependency:
        if name in self.locks:
            async with self.locks[name]:
                return self.dependencies[name]._instance
        else:
            return self.dependencies[name]._instance

    async def start(self, env: dict[str, str]):
        for name, lock_or_none in self.locks.items():
            if lock_or_none:
                async with lock_or_none:
                    await self.dependencies[name].start(env)
            else:
                await self.dependencies[name].start(env)

    async def stop(self, env: dict[str, str]):
        for name, lock_or_none in self.locks.items():
            if lock_or_none:
                async with lock_or_none:
                    await self.dependencies[name].stop(env)
            else:
                await self.dependencies[name].stop(env)
