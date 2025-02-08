from abc import ABC, abstractmethod
from typing import Protocol, AsyncContextManager, TypeVar, Any

DependencyT = TypeVar("DependencyT", bound=AsyncContextManager)


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


class Manager:
    def __init__(self, *dependencies: Dependency):
        self.dependencies = {}
        for dependency in dependencies:
            self.dependencies[dependency.__name__.lower()] = dependency

    async def start(self, env: dict[str, str]):
        for dependency in self.dependencies.values():
            await dependency.start(env)

    def get(self, name: str) -> Dependency:
        return self.dependencies[name]._instance

    async def stop(self, env: dict[str, str]):
        for dependency in self.dependencies.values():
            await dependency.stop(env)
