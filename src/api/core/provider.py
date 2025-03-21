from importlib import import_module
from logging import Logger
from pathlib import Path
from types import ModuleType
from typing import ClassVar

from pydantic import BaseModel
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeMeta

from .deps.dependency import Dependencies
from .router import Router


class Provider:
    dependencies: Dependencies
    metadata: MetaData

    def __repr__(self):
        return f"<Provider {self.name}>"

    @staticmethod
    def _get_package_name(module: ModuleType) -> str:
        if not module.__package__:
            return ""
        parts = module.__package__.split(".")
        return parts[-1] if parts else ""

    @staticmethod
    def _check_relation(
        routers: ModuleType | None,
        tables: ModuleType | None,
        models: list[ModuleType] | ModuleType | None,
        metadata: MetaData,
    ) -> str:
        parents = set()
        if isinstance(models, ModuleType):
            models = [models]
        for obj in [routers, tables, models]:
            if obj:
                if isinstance(obj, ModuleType):
                    name = Provider._get_package_name(obj)
                    if name:
                        parents.add(name)
                elif isinstance(obj, list):
                    for mod in obj:
                        name = Provider._get_package_name(mod)
                        if name:
                            parents.add(name)
        if len(parents) > 1:
            raise ValueError("Routers, tables, and models must have the same parent module")
        parent = parents.pop()
        if parent != metadata.schema:
            raise ValueError("Provider name must match the parent module name")
        return parent

    def __init__(
        self,
        logger: Logger,
        metadata: MetaData,
        routers: ModuleType | None,
        tables: ModuleType | None,
        models: list[ModuleType] | ModuleType | None,
    ):
        self._name = self._check_relation(
            routers, tables, models, metadata
        )  # allows us to use their names interchangeably
        self.metadata = metadata
        self.dependencies = {}
        self._routers = {}
        self._models = {}
        self._tables = {}
        if routers:
            for fname, fn in routers.__dict__.items():
                if hasattr(fn, "info") and hasattr(fn, "metadata"):
                    logger.info(f"Found router {fname}")
                    self._routers[fname] = fn
                    if "requires" in fn.info:
                        logger.info(f"Adding dependencies for {fname}")
                        self.dependencies.update(fn.info["requires"])
        if models:
            if isinstance(models, ModuleType):
                models = [models]
            for mod in models:
                for name, obj in mod.__dict__.items():
                    if isinstance(obj, BaseModel):
                        logger.info(f"Found model {name}")
                        self._models[f"{mod.__name__}.{name}"] = obj  # NOTE addition of module name to avoid collisions
        if tables:
            for name, obj in tables.__dict__.items():
                if isinstance(obj, DeclarativeMeta):
                    logger.info(f"Found table {name}")
                    self._tables[name] = obj

    @property
    def name(self) -> str:
        return self._name

    @property
    def routers(self) -> dict[str, Router]:
        return self._routers

    @property
    def models(self) -> dict[str, BaseModel]:
        return self._models

    @property
    def tables(self) -> dict[str, DeclarativeMeta]:
        return self._tables


class ProviderDirectoryMixin:
    providers: ClassVar[dict[str, Provider]] = {}

    @classmethod
    def load_provider(cls, provider_fp: Path, logger: Logger):
        provider_metadata = None
        provider_routers_mod = None
        provider_models_mods = []
        for fp in provider_fp.glob("*.py"):
            if fp.stem == "routers":
                logger.info(f"Scanning provider {fp.stem} routers")
                provider_routers_mod = import_module(".".join(["src", "ext", provider_fp.stem, fp.stem]))
            elif fp.stem == "tables":
                logger.info(f"Scanning provider {fp.stem} tables")
                provider_tables_mod = import_module(".".join(["src", "ext", provider_fp.stem, fp.stem]))
                if hasattr(provider_tables_mod, "metadata"):
                    provider_metadata = getattr(provider_tables_mod, "metadata")
            elif fp.stem in {"models", "models_generated"}:
                logger.info(f"Scanning provider {fp.stem} models")
                provider_models_mod = import_module(".".join(["src", "ext", provider_fp.stem, fp.stem]))
                provider_models_mods.append(provider_models_mod)
        provider = Provider(
            logger,
            provider_metadata,
            provider_routers_mod,
            provider_tables_mod,
            provider_models_mods,
        )
        cls.providers[provider_fp.name] = provider

    @classmethod
    def router(cls, provider: str, router: str) -> Router:
        return cls.providers[provider].routers[router]

    @classmethod
    def routers(cls, provider: str) -> dict[str, Router]:
        return cls.providers[provider].routers

    @classmethod
    def dependencies(cls, provider: str) -> Dependencies:
        return cls.providers[provider].dependencies

    @classmethod
    def models(cls, provider: str) -> dict[str, BaseModel]:
        return cls.providers[provider].models

    @classmethod
    def tables(cls, provider: str) -> dict[str, DeclarativeMeta]:
        return cls.providers[provider].tables

    @classmethod
    def metadata(cls, provider: str) -> MetaData:
        return cls.providers[provider].metadata
