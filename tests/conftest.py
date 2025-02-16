from typing import AsyncGenerator

import pytest
import pytest_asyncio
import sqlalchemy
from aiohttp import ClientSession
from yarl import URL

from src import api
from src.util import env as env_


@pytest.fixture(scope="session")
def env() -> dict[str, str]:
    return env_.refresh()


@pytest.fixture(scope="session")
def api_root(env: dict[str, str]) -> URL:
    return (
        URL.build(
            scheme="https", 
            host=env["IBKR_HOST"], 
            port=int(env["IBKR_PORT"])
        )
        / "v1"
        / "api"
    )
