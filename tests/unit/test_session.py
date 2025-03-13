import pytest

from src import api

PROVIDERS = ["ibkr"]


@pytest.mark.asyncio
async def test_empty_session():
    session = await api.connect()
    assert session
    assert isinstance(session.providers, dict)
    assert session.session
    assert session.logger
    assert session.env
    assert len(session)


@pytest.mark.asyncio
async def test_session_start():
    session = await api.connect(PROVIDERS)
    assert session
