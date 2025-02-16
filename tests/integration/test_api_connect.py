import pytest

from src import api


@pytest.mark.asyncio
async def test_connect_empty():
    session = await api.connect()
    assert session is not None


@pytest.mark.asyncio
async def test_connect_with_ibkr():
    session = await api.connect(providers=["ibkr"])
    assert session is not None
