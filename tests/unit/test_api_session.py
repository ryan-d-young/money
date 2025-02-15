import pytest

from src import api


@pytest.mark.asyncio
async def test_session_start_stop(env: dict[str, str]):
    session = api.core.Session(
        api.dependencies.HttpClient,
        api.dependencies.DBEngine,
        env=env
    )
    await session.start()
    await session.stop()
