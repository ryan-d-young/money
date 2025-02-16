from contextvars import ContextVar
from typing import AsyncContextManager, ClassVar, Protocol, TypeVar, Iterator

DependencyT = TypeVar("DependencyT", bound=AsyncContextManager)
    

class Dependency[DependencyT](Protocol):
    name: ClassVar[str]
    core: ClassVar[bool] = False
    _instance: ClassVar[DependencyT | None] = None

    async def start(self, env: dict[str, str]) -> None: ...
    async def __aenter__(self) -> DependencyT: ...
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...
    async def stop(self, env: dict[str, str]) -> None: ...


Dependencies = dict[str, Dependency]
DependencyDict = dict[str, ContextVar[DependencyT]]


class DependencyManagerMixin:
    def __init__(self, *dependencies: Dependency):
        dependency_dict = {}
        for dependency in dependencies:
            dependency_dict[dependency.name] = ContextVar(dependency.name)
            dependency_dict[dependency.name].set(dependency)
        self._dependencies = dependency_dict

    def __getitem__(self, name: str) -> ContextVar[DependencyT]:
        return self._dependencies[name]
    
    def __setitem__(self, name: str, value: DependencyT):
        if name not in self._dependencies:
            self._dependencies[name] = ContextVar(name)
        self._dependencies[name].set(value)

    def __iter__(self) -> Iterator[DependencyT]:
        return iter(map(lambda x: x.get(), self._dependencies.values()))

    def __len__(self) -> int:
        return len(self._dependencies)

    def __contains__(self, name: str) -> bool:
        return name in self._dependencies

    def __repr__(self) -> str:
        return f"DependencyManager({', '.join(self._dependencies.keys())})"

    def dependency(self, name: str) -> DependencyT:
        return self[name].get()._instance

    async def start_dependencies(self, env: dict[str, str]):
        for dependency in self:
            await dependency.start(env)

    async def stop_dependencies(self, env: dict[str, str]):
        for dependency in self:
            await dependency.stop(env)

    async def load_dependency(self, *dependencies: Dependency, env: dict[str, str]):
        for dependency in dependencies:
            await dependency.start(env)
            self[dependency.name] = dependency
