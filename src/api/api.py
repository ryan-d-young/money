from src import util

from . import core, dependencies


async def connect(debug: bool = False, *args: core.Dependency, **kwargs: dict[str, str]) -> core.Session:
    logger = util.log.get_logger(__name__, level=0 if debug else 20, write=debug)
    env = util.env.refresh()
    env.update(kwargs)
    session = core.Session(*args, env=env, logger=logger)
    await session.start()
    return session


async def disconnect(session: core.Session) -> core.Session:
    await session.stop()
    return session
