import pytest
import pytest_asyncio
from typing import AsyncGenerator
from aiohttp import ClientSession
from yarl import URL

from src import api, util

@pytest.fixture
def api_root() -> URL:
    _env = util.env.load()
    return (
        URL.build(
            scheme="https", 
            host=_env["IBKR_HOST"], 
            port=int(_env["IBKR_PORT"])
        )
        / "v1"
        / "api"
    )

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[ClientSession, None]:
    env_ = util.env.load()
    session = await api.dependencies.ClientSession.start(env_)
    yield session._instance
    await api.dependencies.ClientSession.stop(env_)


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[api.core.session.Session, None]:
    session = await api.connect()
    yield session
    await api.disconnect(session)
