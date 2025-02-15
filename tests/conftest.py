from typing import AsyncGenerator

import pytest
import pytest_asyncio
import sqlalchemy
from aiohttp import ClientSession
from yarl import URL

from src import api, util


@pytest.fixture(scope="session")
def env() -> dict[str, str]:
    return util.env.refresh()


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


@pytest_asyncio.fixture
async def http_client(env: dict[str, str]) -> AsyncGenerator[ClientSession, None]:
    session = await api.dependencies.HttpClient.start(env)
    yield session._instance
    await api.dependencies.HttpClient.stop(env)


@pytest_asyncio.fixture
async def db_engine(env: dict[str, str]) -> AsyncGenerator[sqlalchemy.Engine, None]:
    engine = await api.dependencies.DBEngine.start(env)
    yield engine._instance
    await api.dependencies.DBEngine.stop(env)


@pytest_asyncio.fixture
async def dependencies(
    db_engine: sqlalchemy.Engine, 
    http_client: ClientSession
) -> AsyncGenerator[tuple[sqlalchemy.Engine, ClientSession], None]:
    return db_engine, http_client


@pytest_asyncio.fixture
async def session(dependencies: tuple[sqlalchemy.Engine, ClientSession]) -> AsyncGenerator[api.core.Session, None]:
    session = await api.connect(*dependencies)
    yield session
    await api.disconnect(session)
