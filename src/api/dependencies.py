import aiohttp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .core import dependency


class ClientSession(dependency.Dependency[aiohttp.ClientSession]):
    @classmethod
    async def start(cls, env: dict[str, str]):
        cls._instance = aiohttp.ClientSession()
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.close()
        cls._instance = None
        

class DBEngine(dependency.Dependency[AsyncEngine]):
    @classmethod
    async def start(cls, env: dict[str, str]):
        url = (
            f"postgresql+asyncpg://"
            f"{env['DBUSER']}:{env['DBPASS']}@"
            f"{env['DBHOST']}:{env['DBPORT']}"
        )
        cls._instance = create_async_engine(url)

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.dispose()
        cls._instance = None
        return cls
