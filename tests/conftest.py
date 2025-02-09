import pytest
import pytest_asyncio
from typing import AsyncGenerator
from aiohttp import ClientSession
import sqlalchemy
from yarl import URL

from src import api, util


@pytest.fixture
def env() -> dict[str, str]:
    return util.env.load()


@pytest.fixture
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
    yield session
    await api.dependencies.HttpClient.stop(env)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[api.core.session.Session, None]:
    session = await api.connect()
    yield session
    await api.disconnect(session)


@pytest_asyncio.fixture
async def db_engine(env: dict[str, str]) -> AsyncGenerator[sqlalchemy.Engine, None]:
    engine = await api.dependencies.DBEngine.start(env)
    yield engine
    await api.dependencies.DBEngine.stop(env)


@pytest_asyncio.fixture
async def dependencies(
    db_engine: sqlalchemy.Engine, 
    http_client: ClientSession
) -> AsyncGenerator[tuple[sqlalchemy.Engine, ClientSession], None]:
    return db_engine, http_client
