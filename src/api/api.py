from src import const, util
from . import dependencies, core


async def _connect(env: dict[str, str]) -> dependencies.DependencyManager:
    db_engine = await dependencies.DBEngine.start(env)
    http_session = await dependencies.ClientSession.start(env)
    return dependencies.DependencyManager(db_engine, http_session)


async def connect():
    env = util.env.load()
    dependency_manager = await _connect(env)
    registry = core.Registry.scan(const.EXT_ROOT)
        
    return dependency_manager


async def disconnect(dependency_manager: dependencies.DependencyManager):
    await dependency_manager.stop()