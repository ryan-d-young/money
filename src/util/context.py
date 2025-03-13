import os
from contextvars import ContextVar
from functools import cache
from pathlib import Path
from typing import Any

import dotenv
import tomlkit

HOME = Path.home()
ROOT = Path.cwd()
PROJECT = ROOT / "src"
PROVIDERS = PROJECT / "ext"

parent_dir: ContextVar[Path] = ContextVar("parent_dir", default=HOME)
project_name: ContextVar[str] = ContextVar("project_name", default="root")


@cache
def project_root() -> Path:
    return parent_dir.get() / project_name.get()


@cache
def settings() -> dict[str, Any]:
    settings = {}
    if (fp := project_root() / "settings.toml").exists():
        with Path.open(fp, "rb") as f:
            settings = tomlkit.load(f)
    return settings


@cache
def env(**kwargs: dict[str, str]) -> dict[str, str]:
    dotenv.load_dotenv(project_root() / ".env")
    env_ = dict(os.environ)
    env_.update(kwargs)
    return env_
