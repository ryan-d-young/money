from typing import AsyncContextManager, ClassVar, Protocol, TypeVar

DependencyT = TypeVar("DependencyT", bound=AsyncContextManager)


class Dependency[DependencyT](Protocol):
    name: ClassVar[str]
    _instance: ClassVar[DependencyT | None] = None

    async def start(self, env: dict[str, str]) -> None: ...
    async def __aenter__(self): ...
    async def __aexit__(self): ...
    async def stop(self, env: dict[str, str]) -> None: ...


class Manager:
    def __init__(self, *dependencies: Dependency):
        self.dependencies = {}
        for dependency in dependencies:
            self.dependencies[dependency.name] = dependency

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dependencies})"

    async def start(self, env: dict[str, str]):
        for dependency in self.dependencies.values():
            await dependency.start(env)

    def get(self, name: str) -> Dependency:
        return self.dependencies[name]._instance

    async def stop(self, env: dict[str, str]):
        for dependency in self.dependencies.values():
            await dependency.stop(env)
