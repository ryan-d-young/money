import os
from contextvars import ContextVar
from functools import cache
from pathlib import Path
from typing import Any

import dotenv
import yaml

ROOT = Path.cwd()
PROJECT = ROOT / "src"
PROVIDERS = PROJECT / "ext"

parent_dir: ContextVar[Path] = ContextVar("parent_dir")
project_name: ContextVar[str] = ContextVar("project_name")


@cache
def project_root() -> Path:
    parent = parent_dir.get() or Path.home()
    return parent / project_name.get()


@cache
def config() -> dict[str, Any]:
    if (fp := project_root() / "config.yaml").exists():
        with Path.open(fp, "r") as f:
            config = yaml.safe_load(f)
    else:
        config = {}
        with Path.open(fp, "w") as f:
            yaml.dump(config, f)
    return config


@cache
def env(**kwargs: dict[str, str]) -> dict[str, str]:
    dotenv.load_dotenv(project_root() / ".env")
    env_ = dict(os.environ)
    env_.update(kwargs)
    return env_
