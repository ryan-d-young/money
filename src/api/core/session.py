import asyncio
from functools import partial
from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.request import Request
from api.core.response import Response
from src import const
from . import Dependency, Router, Registry


class DependencyManager:
    def __init__(self, *dependencies: Dependency):
        self.dependencies = {}
        self.locks = {}
        for dependency in dependencies:
            self.dependencies[dependency.name] = dependency
            if dependency.exclusive:
                self.locks[dependency.name] = asyncio.Lock()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dependencies})"

    async def get(self, name: str) -> Dependency:
        if name in self.locks:
            async with self.locks[name]:
                return self.dependencies[name]._instance
        else:
            return self.dependencies[name]._instance

    async def restart(self, name: str):
        if name in self.locks:
            async with self.locks[name]:
                await self.dependencies[name].stop(self._env)
                await self.dependencies[name].start(self._env)
        else:
            await self.dependencies[name].stop(self._env)
            await self.dependencies[name].start(self._env)

    async def stop(self, env: dict[str, str]):
        for dependency in self.dependencies.values():
            await dependency.stop(env)


class Session:
    def __init__(self, *dependencies: Dependency, env: dict[str, str], logger: Logger):
        self.dependency_manager = DependencyManager(*dependencies)
        self.logger = logger
        self.registry = Registry.scan(const.PROVIDERS, logger=self.logger)
        self._env = dict(env)
        self._db_session = AsyncSession(self.dependency_manager.get("db_engine"))

    async def start(self):
        await self.dependency_manager.start(self._env)
        self.logger.info("Session started")
        return self

    async def stop(self):
        await self.dependency_manager.stop(self._env)
        await self._db_session.close()
        self.logger.info("Session stopped")
        return self

    async def dependency(self, name: str) -> Dependency:
        return await self.dependency_manager.get(name)

    async def router(self, provider: str, name: str) -> Router:
        router = self.registry.router(provider, name)
        return await self.inject(router)

    @property
    def env(self) -> dict[str, str]:
        return dict(self._env)

    @property
    def session(self) -> AsyncSession:
        return self._db_session

    @session.setter
    def session(self, session: AsyncSession):
        self._db_session = session

    async def inject(self, router: Router) -> Router:
        deps = [await self.dependency(name) for name in router.info.requires]
        return partial(router, *deps)

    async def call(self, provider: str, router: str, request: Request) -> AsyncGenerator[Response, None]:  # type: ignore
        router = await self.router(provider, router)
        router = await self.inject(router)
        async for response in router(request):
            yield response

    def __call__(self, provider: str, router: str, request: Request) -> AsyncGenerator[Response, None]:  # type: ignore
        self.logger.info(f"Calling {provider}.{router} with {request}")
        return self.call(provider, router, request)
