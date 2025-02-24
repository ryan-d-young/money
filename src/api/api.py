from asyncio import AbstractEventLoop, get_running_loop
from logging import Logger
from pathlib import Path

from src import util

from .core.deps import core_dependencies
from .session import Session


def _set_context(parent_directory: Path | None, project_name: str | None):
    util.context.parent_dir.set(parent_directory or Path.home())
    util.context.project_name.set(project_name or "root")


async def connect(
    providers: list[str] | bool | str = True,
    logger: Logger | None = None,
    loop: AbstractEventLoop | None = None,
    parent_directory: Path | None = None,
    project_name: str | None = None,
    **env_vars: dict[str, str],
) -> Session:
    """Connect to the API. Shadows `Session.start`.

    Args:
        providers (list[str] | bool, optional): Providers to load. If a list is provided, only the providers in the list
            will be loaded. If True, all providers will be loaded. If False, no providers will be loaded.
            Defaults to True.
        logger (Logger | None, optional): Logger to use. Defaults to None.
        loop (AbstractEventLoop | None, optional): Event loop to use. Defaults to None.
        parent_directory (Path | None, optional): Parent directory to use. Defaults to None.
        project_name (str | None, optional): Project name to use. Defaults to None.
        **env_vars (dict[str, str]): Environment variables to override.

    Returns:
        Session: Session instance

    """
    _set_context(parent_directory, project_name)

    logger = logger or util.log.get_logger(__name__)
    env = util.context.env(**env_vars)
    logger.info("Environment loaded")

    loop = loop or get_running_loop()
    session = Session(
        logger=logger,
        env=env,
        dependencies=core_dependencies,
        loop=loop,
        provider_dir=util.context.PROVIDERS,
    )
    await session.start(providers=providers)

    session.logger.info("Session initialized")

    return session
