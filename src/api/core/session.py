from logging import Logger
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.util import log
from src.const import PROVIDERS
from .dependency import Dependency, DependencyManager
from .provider import Registry
from .request import Request, RequestKwargs
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
        self._db_session = AsyncSession(self["db"]._instance)

    def __getitem__(self, name: str) -> Dependency:
        return self.dependency_manager[name]

    def router(self, provider: str, name: str) -> Router:
        return self.registry.router(provider, name)

    @property
    def env(self) -> dict[str, str]:
        return dict(self._env)

    @property
    def session(self) -> AsyncSession:
        return self._db_session

    @session.setter
    def session(self, session: AsyncSession):
        self._db_session = session

    async def start(self):
        await self.dependency_manager.start(self._env)
        self.logger.info("Session started")
        return self

    async def stop(self):
        await self.dependency_manager.stop(self._env)
        await self._db_session.close()
        self.logger.info("Session stopped")
        return self

    def __call__(self, provider: str, router: str, **kwargs: RequestKwargs) -> AsyncGenerator[Response, None]:
        router: Router = self.router(provider, router)        
        router_kwargs = {}
        if router.info["requires"]:
            deps = {
                kwd: self[dep.name]._instance
                for kwd, dep 
                in router.info["requires"].items()
            }
            router_kwargs.update(deps)
        if router.info["accepts"]:
            request = Request(router.info["accepts"])
            request.make(**kwargs)
            router_kwargs.update(request=request.data)
        return router(**router_kwargs)
