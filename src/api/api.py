from logging import Logger
from src import util
from .dependencies import core_dependencies
from .session import Session


async def connect(
    providers: list[str] | bool | str = True, 
    logger: Logger | None = None, 
    **env_vars: dict[str, str]
) -> Session:
    """Connect to the API. Shadows `Session.start`.

    Args:
        providers (list[str] | bool, optional): Providers to load. If a list is provided, only the providers in the list
            will be loaded. If True, all providers will be loaded. If False, no providers will be loaded.
            Defaults to True.
        logger (Logger | None, optional): Logger to use. Defaults to None.
        **env_vars (dict[str, str]): Environment variables to override.
    Returns:
        Session: Session instance
    """
    logger = logger or util.log.get_logger(__name__)
    env = util.env.refresh()
    env.update(env_vars)
    logger.info("Environment loaded")

    session = Session(logger=logger, env=env, dependencies=core_dependencies)
    await session.start(providers=providers)
    
    session.logger.info("Session initialized")

    return session

