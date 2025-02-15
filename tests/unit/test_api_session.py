import pytest

from src import api, const, util


def test_make_dependency_manager(dependencies: tuple[api.core.Dependency]):
    manager = api.core.DependencyManager(*dependencies)
    for dependency in dependencies:
        assert isinstance(
            manager.acquire(dependency.name),
            dependency.__orig_bases__[0].__args__[0],  # type: ignore
        )


def test_build_registry():
    registry = api.core.Registry.scan(
        const.PROVIDERS, logger=util.log.get_logger("test", write=False)
    )
    assert "ibkr" in registry.providers
    assert len(registry.providers["ibkr"].routers) > 0
    assert len(registry.providers["ibkr"].tables) > 0


@pytest.mark.asyncio
async def test_session_start_stop(
    dependencies: tuple[api.core.Dependency], env: dict[str, str]
):
    session = api.core.Session(
        *dependencies, env=env, logger=util.log.get_logger("test", write=False)
    )
    await session.start()
    await session.stop()
