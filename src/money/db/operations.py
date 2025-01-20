from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


def engine_from_creds(
    host: str, port: int, 
    user: str, pswd: str, 
    protocol: str = "postgresql", 
    **kwargs
) -> AsyncEngine:
    url = f"{protocol}://{user}:{pswd}@{host}:{port}"
    engine = create_async_engine(url=url, **kwargs)
    return engine
