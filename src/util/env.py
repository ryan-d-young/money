import os
from typing import Any
from functools import lru_cache

import dotenv

from src.const import ROOT


@lru_cache(maxsize=None)
def load() -> dict[str, str]:
    return os.environ


def get(key: str) -> Any:
    try:
        return load()[key]
    except KeyError:
        raise KeyError(f"Environment variable {key} not found")


def refresh() -> dict[str, str]:
    dotenv.load_dotenv(ROOT / ".env")
    load.cache_clear()
    return load()
