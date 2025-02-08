import pytest
import pytest_asyncio
from typing import AsyncGenerator
from aiohttp import ClientSession
from yarl import URL

from src.util import env 
from src.api import dependencies


@pytest.fixture
def api_root() -> URL:
    _env = env.load()
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
    env_ = env.load()
    session = await dependencies.ClientSession.start(env_)
    yield session._instance
    await dependencies.ClientSession.stop(env_)
    