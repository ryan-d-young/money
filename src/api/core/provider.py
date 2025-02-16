from pathlib import Path
from typing import ClassVar, TypeVar
from types import ModuleType
from importlib import import_module
from logging import Logger

from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import MetaData

from .router import Router
from .dependency import Dependencies


class Provider:
    routers: dict[str, Router]
    dependencies: Dependencies
    metadata: MetaData | None = None

    def __repr__(self):
        return f"<Provider {self.name}>"

    def __init__(self, logger: Logger, metadata: MetaData, routers: ModuleType | None):
        self.metadata = metadata
        self.dependencies = {}
        self._routers = {}
        if routers:
            for fname, fn in routers.__dict__.items():
                if hasattr(fn, "info") and hasattr(fn, "metadata"):
                    logger.info(f"Found router {fname}")
                    self._routers[fname] = fn
                    if "requires" in fn.info:
                        logger.info(f"Adding dependencies for {fname}")
                        self.dependencies.update(fn.info["requires"])

    @property
    def routers(self) -> dict[str, Router]:
        return self._routers

    @property
    def tables(self) -> dict[str, DeclarativeMeta]:
        return self._tables

    @property
    def name(self) -> str:
        return self.metadata.schema


ProviderDictT = TypeVar("ProviderDictT", bound=dict[str, Provider])


class ProviderDirectoryMixin:
    providers: ClassVar[ProviderDictT] = {}

    @classmethod
    def load_provider(cls, provider: Path, logger: Logger):
        provider_metadata = None
        provider_routers_mod = None
        for fp in provider.glob("*.py"):
            if fp.stem == "routers":
                logger.info(f"Scanning provider {fp.stem} routers")
                provider_routers_mod = import_module(
                    ".".join(["src", "ext", provider.stem, fp.stem])
                )
            elif fp.stem == "tables":
                logger.info(f"Scanning provider {fp.stem} tables")
                provider_tables_mod = import_module(
                    ".".join(["src", "ext", provider.stem, fp.stem])
                )
                if hasattr(provider_tables_mod, "metadata"):
                    provider_metadata = getattr(provider_tables_mod, "metadata")
        provider = Provider(logger, provider_metadata, provider_routers_mod)
        cls.providers[provider.name] = provider

    @classmethod
    def router(cls, provider: str, router: str) -> Router:
        return cls.providers[provider].routers[router]

    @classmethod
    def routers(cls, provider: str) -> dict[str, Router]:
        return cls.providers[provider].routers

    @classmethod
    def dependencies(cls, provider: str) -> Dependencies:
        return cls.providers[provider].dependencies
