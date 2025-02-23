import os
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from typing import Any

import dotenv
import yaml

ROOT = Path(".").resolve()
PROJECT = ROOT / "src"
PROVIDERS = PROJECT / "ext"

parent_dir: ContextVar[Path] = ContextVar("parent_dir")
project_name: ContextVar[str] = ContextVar("project_name")


@lru_cache(maxsize=None)
def project_root() -> Path:
    parent = parent_dir.get() or Path.home()
    return parent / project_name.get()


@lru_cache(maxsize=None)
def config() -> dict[str, Any]:
    if (fp := project_root() / "config.yaml").exists():
        with open(fp, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
        with open(fp, "w") as f:
            yaml.dump(config, f)
    return config


@lru_cache(maxsize=None)
def env(**kwargs: dict[str, str]) -> dict[str, str]:
    dotenv.load_dotenv(project_root() / ".env")
    env = dict(os.environ)
    env.update(kwargs)
    return env
