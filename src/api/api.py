from src.data.util import log
from . import dependencies, core


async def _connect(env: dict[str, str]):
    db_engine = await dependencies.DBEngine.start(env)
    http_session = await dependencies.ClientSession.start(env)
    