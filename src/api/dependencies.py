import aiohttp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .core.protocols import Dependency


class ClientSession(Dependency[aiohttp.ClientSession]):
    @classmethod
    async def start(cls, env: dict[str, str]):
        cls._instance = aiohttp.ClientSession()

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.close()
        cls._instance = None
        

class DBEngine(Dependency[AsyncEngine]):
    @classmethod
    async def start(cls, env: dict[str, str]):
        url = (
            f"postgresql+asyncpg://"
            f"{env['dbuser']}:{env['dbpass']}@"
            f"{env['dbhost']}:{env['dbport']}"
        )
        cls._instance = create_async_engine(url)

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.dispose()
        cls._instance = None
        