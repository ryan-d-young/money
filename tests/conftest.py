import asyncio

import pytest
import pytest_asyncio
from yarl import URL

from src import api
from util import fs as env_


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def env() -> dict[str, str]:
    _env = env_.refresh()
    _env["_loop"] = asyncio.get_running_loop()
    return _env


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def api_root(env: dict[str, str]) -> URL:
    return (
        URL.build(
            scheme="https", 
            host=env["IBKR_HOST"], 
            port=int(env["IBKR_PORT"])
        )
        / "v1"
        / "api"
    )


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def ibkr_api_session(env: dict[str, str]) -> api.Session:
    return await api.connect(providers=["ibkr"], env=env)
