from logging import Logger
from typing import AsyncGenerator, Unpack

from src import const, util
from .core import Router, Response, Request, RequestKwargs, RequestModelT, Dependency
from .core.orm import OrmSessionMixin
from .core.provider import ProviderDirectoryMixin
from .core.dependency import DependencyManagerMixin


class Session(ProviderDirectoryMixin, OrmSessionMixin, DependencyManagerMixin):
    def __init__(
        self, *, 
        logger: Logger | None = None, 
        env: dict[str, str] | None = None, 
        dependencies: list[Dependency] | None = None
    ):
        dependencies = dependencies or []
        DependencyManagerMixin.__init__(self, *dependencies)
        self.logger = logger or util.log.get_logger(__name__)
        self._env = env or util.env.refresh()

    @staticmethod
    def _resolve_providers(providers: list[str] | bool | str) -> list[str]:
        if isinstance(providers, bool):
            if providers:
                providers = [p.stem for p in const.PROVIDERS.glob("*.py")]
            else:
                providers = []
        elif isinstance(providers, str):
            providers = [providers]
        return providers

    @classmethod
    def load_providers(cls, providers: list[str] | bool, logger: Logger) -> None:
        providers = cls._resolve_providers(providers)
        for provider in providers:
            fp = const.PROVIDERS / provider
            if fp.exists():
                cls.load_provider(fp, logger)
            else:
                logger.warning(f"Provider {provider} not found")

    async def load_dependencies(self, providers: list[str]):
        for provider in providers:
            for name, dependency in self.dependencies(provider).items():
                await dependency.start(self.env)
                self[name] = dependency
        await self.start_dependencies(self.env)

    async def start(self, providers: list[str] | bool = True) -> "Session":
        providers = self._resolve_providers(providers)
        self.load_providers(providers, self.logger)
        await self.load_dependencies(providers)
        await self.init_db(
            dbengine=self.dependency("db"), 
            provider_metadata=[p.metadata for p in self.providers.values()]
        )
        return self

    async def stop(self, commit: bool = True) -> "Session":
        await self.stop_dependencies(self._env)
        await self.stop_db(commit)
        return self

    @property
    def env(self) -> dict[str, str]:
        return dict(self._env)

    def _inject(self, router: Router, kwargs: RequestKwargs | Unpack[RequestModelT]) -> dict:
        router_kwargs = {}
        if router.info["accepts"]:
            request = Request(router.info["accepts"])
            request.make(**kwargs)
            router_kwargs.update(**request.data)
        if router.info["requires"]:
            deps = {
                kwd: self.dependency(dep.name)
                for kwd, dep 
                in router.info["requires"].items()
            }
            router_kwargs.update(deps)
        return router_kwargs

    def __call__(
        self, 
        provider: str, 
        router: str, 
        **kwargs: RequestKwargs | Unpack[RequestModelT]
    ) -> AsyncGenerator[Response, None]:
        router = self.providers.router(provider, router)
        kwargs = self._inject(router, kwargs)
        return router(**kwargs)

    def __repr__(self) -> str:
        return f"<Session({', '.join(self.providers.keys())})>"
