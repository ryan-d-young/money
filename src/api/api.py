from logging import Logger
from src import util
from .dependencies import core_dependencies
from .session import Session
import asyncio
from asyncio import AbstractEventLoop


async def connect(
    providers: list[str] | bool | str = True, 
    logger: Logger | None = None,
    loop: AbstractEventLoop | None = None,
    **env_vars: dict[str, str]
) -> Session:
    """Connect to the API. Shadows `Session.start`.

    Args:
        providers (list[str] | bool, optional): Providers to load. If a list is provided, only the providers in the list
            will be loaded. If True, all providers will be loaded. If False, no providers will be loaded.
            Defaults to True.
        logger (Logger | None, optional): Logger to use. Defaults to None.
        loop (AbstractEventLoop | None, optional): Event loop to use. Defaults to None.
        **env_vars (dict[str, str]): Environment variables to override.
    Returns:
        Session: Session instance
    """
    logger = logger or util.log.get_logger(__name__)
    env = util.env.refresh()
    env.update(env_vars)
    logger.info("Environment loaded")

    loop = loop or asyncio.get_running_loop()
    session = Session(logger=logger, env=env, dependencies=core_dependencies, loop=loop)
    await session.start(providers=providers)
    
    session.logger.info("Session initialized")

    return session

