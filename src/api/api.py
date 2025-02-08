from src import util
from . import dependencies, core


async def connect(debug: bool = False) -> core.Session:
    env = util.env.load()
    logger = util.log.get_logger(
        __name__, 
        level=0 if debug else 20, 
        write=debug
    )
    session = await core.Session(
        dependencies.ClientSession, 
        dependencies.DBEngine,
        env=env,
        logger=logger
    ).start()
    return session


async def disconnect(session: core.Session) -> core.Session:
    await session.stop()
    return session
