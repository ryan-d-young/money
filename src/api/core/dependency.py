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


class DependencyManager:
    def __init__(self, *dependencies: Dependency):
        dependency_dict = {}
        for dependency in dependencies:
            dependency_dict[dependency.name] = dependency
        self._dependencies = dependency_dict

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dependencies})"

    def __getitem__(self, name: str) -> Dependency:
        return self._dependencies[name]

    async def start(self, env: dict[str, str]):
        for dependency in self._dependencies.values():
            await dependency.start(env)

    async def stop(self, env: dict[str, str]):
        for dependency in self._dependencies.values():
            await dependency.stop(env)
