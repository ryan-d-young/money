from asyncio import AbstractEventLoop
from collections.abc import Iterator
from contextvars import ContextVar

from .dependency import Dependency


class DependencyManagerMixin:
    def __init__(self, *dependencies: Dependency):
        dependency_dict = {}
        for dependency in dependencies:
            dependency_dict[dependency.name] = ContextVar(dependency.name)
            dependency_dict[dependency.name].set(dependency)
        self._dependencies = dependency_dict

    def __getitem__(self, name: str) -> ContextVar[Dependency]:
        return self._dependencies[name]

    def __setitem__(self, name: str, value: Dependency):
        if name not in self._dependencies:
            self._dependencies[name] = ContextVar(name)
        self._dependencies[name].set(value)

    def __iter__(self) -> Iterator[Dependency]:
        return iter(map(lambda x: x.get(), self._dependencies.values()))

    def __len__(self) -> int:
        return len(self._dependencies)

    def __contains__(self, name: str) -> bool:
        return name in self._dependencies

    def __repr__(self) -> str:
        return f"DependencyManager({', '.join(self._dependencies.keys())})"

    def dependency(self, name: str) -> Dependency:
        return self[name].get()

    async def start_dependencies(self, env: dict[str, str], loop: AbstractEventLoop):
        for dependency in self:
            await dependency.start(env, loop)

    async def stop_dependencies(self, env: dict[str, str]):
        for dependency in self:
            await dependency.stop(env)

    async def load_dependency(self, *dependencies: Dependency, env: dict[str, str], loop: AbstractEventLoop):
        for dependency in dependencies:
            await dependency.start(env, loop)
            self[dependency.name] = dependency
