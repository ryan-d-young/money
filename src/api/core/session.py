from functools import partial
from logging import Logger

from src import const
from . import dependency, router


class Session:
    def __init__(self, *dependencies: dependency.Dependency, env: dict[str, str], logger: Logger):
        self._env = env
        self.dependency_manager = dependency.Manager(*dependencies)
        self.logger = logger
        self.registry = router.Registry.scan(const.EXT_ROOT, logger=self.logger)
    
    async def start(self):
        await self.dependency_manager.start(self._env)
        self.logger.info("Session started")
        return self

    async def stop(self):
        await self.dependency_manager.stop(self._env)
        self.logger.info("Session stopped")
        return self

    def dependency(self, name: str) -> dependency.Dependency:
        return self.dependency_manager.get(name)

    def router(self, name: str) -> router.Router:
        return self.registry.get(name)

    @property
    def env(self) -> dict[str, str]:
        return self._env

    def inject(self, router: router.Router) -> router.Router:
        deps = [
            self.dependency(name) 
            for name in router.info.requires
        ]
        return partial(router, *deps)
