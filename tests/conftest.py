import pytest
import pytest_asyncio
from yarl import URL
from aiohttp import ClientSession

from src.util import env 


@pytest_asyncio.fixture
async def http_client() -> ClientSession:  # type: ignore
    async with ClientSession() as session:
        yield session


@pytest.fixture
def api_root() -> URL:
    _env = env.load()
    return URL.build(_env["IBKR_HOST"], port=_env["IBKR_PORT"])
