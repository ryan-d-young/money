from pathlib import Path
from typing import ClassVar
from types import ModuleType
from importlib import import_module
from logging import Logger

from sqlalchemy import Table

from src.util import log
from .router import Router


class Provider:
    routers: dict[str, Router]

    def __repr__(self):
        return f"<Provider {self.name}>"

    def __init__(self, mod: ModuleType):
        self.name = __name__.split(".")[-1]
        self._logger = log.get_logger(self.name)
        self.routers = {}
        for fname, fn in mod.__dict__.items():
            if hasattr(fn, "info") and hasattr(fn, "context"):
                self._logger.info(f"Found router {fname}")
                self.routers[fname] = fn

    @property
    def tables(self) -> dict[str, Table]:
        tbl = {}
        for router in self.routers.values():
            if "stores" in router.info:
                tbl[router.info["stores"].__tablename__] = router.info["stores"]  # type: ignore
        return tbl


class Registry:
    providers: ClassVar[dict[str, Provider]] = {}

    def __repr__(self):
        return f"<Registry {self.providers}>"

    @classmethod
    def scan(cls, ext_root: Path, logger: Logger):
        cls._logger = logger
        for fp_provider in ext_root.glob("*"):
            for fp_router in fp_provider.glob("*.py"):
                if fp_router.stem == "routers":
                    cls._logger.info(f"Scanning provider {fp_provider.stem}")
                    mod = import_module(
                        ".".join(["src", "ext", fp_provider.stem, fp_router.stem])
                    )
                    cls.providers[fp_provider.stem] = Provider(mod)
        return cls

    @classmethod
    def router(cls, provider: str, router: str) -> Router:
        return cls.providers[provider].routers[router]

    @classmethod
    def table(cls, provider: str, table: str) -> Table:
        return cls.providers[provider].tables[table]
