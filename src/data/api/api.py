from .dependencies import ClientSession, DBEngine


async def _connect(env: dict[str, str]):
    db_engine = await DBEngine.start(env)
    http_session = await ClientSession.start(env)