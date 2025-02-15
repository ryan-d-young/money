from functools import partial
from logging import Logger
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.util import log
from src.const import PROVIDERS
from .dependency import Dependency, DependencyManager
from .provider import Registry
from .request import Request
from .response import Response
from .router import Router


class Session:
    def __init__(
        self,
        *dependencies: Dependency, 
        env: dict[str, str],
        logger: Logger | None = None,
    ):
        self.dependency_manager = DependencyManager(*dependencies)
        self.logger = logger or log.get_logger(__name__)
        self.registry = Registry.scan(PROVIDERS, logger=self.logger)
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
        return await self.dependency_manager.acquire(name)

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

    async def call(
        self, provider: str, router: str, request: Request
    ) -> AsyncGenerator[Response, None]:
        router = await self.router(provider, router)
        router = await self.inject(router)
        async for response in router(request):
            yield response

    def __call__(
        self, provider: str, router: str, request: Request
    ) -> AsyncGenerator[Response, None]:  
        self.logger.info(f"Calling {provider}.{router} with {request}")
        return self.call(provider, router, request)
