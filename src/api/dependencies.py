import aiohttp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from typing import ClassVar
from .core import dependency


class HttpClient(dependency.Dependency[aiohttp.ClientSession]):
    _instance: ClassVar[aiohttp.ClientSession | None] = None
    name = "http_client"

    @classmethod
    async def start(cls, env: dict[str, str]):
        cls._instance = aiohttp.ClientSession()
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.close()
        cls._instance = None
        return cls


class DBEngine(dependency.Dependency[AsyncEngine]):
    _instance: ClassVar[AsyncEngine | None] = None
    name = "db_engine"

    @classmethod
    async def start(cls, env: dict[str, str]):
        url = (
            f"postgresql+asyncpg://"
            f"{env['DBUSER']}:{env['DBPASS']}@"
            f"{env['DBHOST']}:{env['DBPORT']}"
        )
        cls._instance = create_async_engine(url)
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.dispose()
        cls._instance = None
        return cls
