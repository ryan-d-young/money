import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def http_client():
    from aiohttp import ClientSession
    async with ClientSession() as session:
        yield session

