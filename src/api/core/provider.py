from src.util import log

from typing import ModuleType

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
