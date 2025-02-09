from functools import partial
from logging import Logger

from src import const
from .dependency import Dependency, Manager
from .router import Router, Registry


class Session:
    def __init__(self, *dependencies: Dependency, env: dict[str, str], logger: Logger):
        self._env = env
        self.dependency_manager = Manager(*dependencies)
        self.logger = logger
        self.registry = Registry.scan(const.PROVIDERS, logger=self.logger)
    
    async def start(self):
        await self.dependency_manager.start(self._env)
        self.logger.info("Session started")
        return self

    async def stop(self):
        await self.dependency_manager.stop(self._env)
        self.logger.info("Session stopped")
        return self

    def dependency(self, name: str) -> Dependency:
        return self.dependency_manager.get(name)

    def router(self, provider: str, name: str) -> Router:
        router = self.registry.router(provider, name)
        return self.inject(router)

    @property
    def env(self) -> dict[str, str]:
        return self._env

    def inject(self, router: Router) -> Router:
        deps = [
            self.dependency(name) 
            for name in router.info.requires
        ]
        return partial(router, *deps)
