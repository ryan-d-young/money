from pathlib import Path
from asyncio import AbstractEventLoop
from logging import Logger
from typing import AsyncGenerator, Unpack

from sqlalchemy import Table

from .core.dependency import Dependency, DependencyManagerMixin
from .core.orm import OrmSessionMixin, metadata
from .core.provider import ProviderDirectoryMixin
from .core.request import Request, RequestKwargs, RequestModelT
from .core.response import Response
from .core.router import Router


class Session(ProviderDirectoryMixin, OrmSessionMixin, DependencyManagerMixin):
    """
    A session for the API. Encapsulates the environment, loop, and dependencies.
    """

    def __init__(
        self,
        provider_dir: Path,
        loop: AbstractEventLoop,
        logger: Logger,
        env: dict[str, str],
        dependencies: list[Dependency] | None = None,
    ):
        dependencies = dependencies or []
        DependencyManagerMixin.__init__(self, *dependencies)
        self.logger = logger
        self._env = env
        self._loop = loop
        self._provider_dir = provider_dir

    def _resolve_providers(self, providers: list[str] | bool | str) -> list[str]:
        if isinstance(providers, bool):
            if providers:
                providers = [p.stem for p in self._provider_dir.glob("*.py")]
            else:
                providers = []
        elif isinstance(providers, str):
            providers = [providers]
        return providers

    def _load_providers(self, providers: list[str] | bool, logger: Logger) -> None:
        providers = self._resolve_providers(providers)
        for provider in providers:
            fp = self._provider_dir / provider
            if fp.exists():
                self.load_provider(fp, logger)
            else:
                logger.warning(f"Provider {provider} not found")

    async def _load_dependencies(self, providers: list[str]):
        for provider in providers:
            for dependency in self.dependencies(provider).values():
                await dependency.start(self.env, self.loop)
                self[dependency.name] = dependency
        await self.start_dependencies(self.env, self.loop)

    async def start(self, providers: list[str] | bool = True) -> "Session":
        providers = self._resolve_providers(providers)
        self._load_providers(providers, self.logger)
        await self._load_dependencies(providers)
        await self.init_db(
            dbengine=self.dependency("db"),
            provider_metadata=[p.metadata for p in self.providers.values()],
        )
        return self

    async def stop(self, commit: bool = True) -> "Session":
        await self.stop_dependencies(self._env)
        await self.stop_db(commit)
        return self

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def env(self) -> dict[str, str]:
        return dict(self._env)

    def table(self, table_name: str, provider: str | None = None) -> Table:
        if provider:
            table_metadata = self.providers[provider].metadata
        else:
            table_metadata = metadata
        return self._table(table_name, table_metadata)

    def _inject_request(self, router: Router) -> dict:
        deps = {
            kwd: self.dependency(dep.name)
            for kwd, dep in router.info["requires"].items()
        }
        return deps

    @staticmethod
    def _populate_request(
        router: Router, **kwargs: RequestKwargs | Unpack[RequestModelT]
    ) -> dict:
        request = Request(router.info["accepts"])
        request.make(**kwargs)
        return request

    async def __call__(
        self,
        provider: str,
        router: str,
        **kwargs: RequestKwargs | Unpack[RequestModelT],
    ) -> AsyncGenerator[Response, None]:
        router_instance = self.router(provider, router)
        deps = self._inject_request(router_instance)
        request = self._populate_request(router_instance, **kwargs)
        async for response in router_instance(request, **deps):
            yield response

    def __repr__(self) -> str:
        return f"<Session({', '.join(self.providers.keys())})>"
