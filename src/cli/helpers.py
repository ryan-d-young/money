async def new_session():
    from src.api import connect
    session = await connect()
    return session
