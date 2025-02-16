from typing import ClassVar

import aiohttp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .core import dependency


class HttpClient(dependency.Dependency[aiohttp.ClientSession]):
    _instance: ClassVar[aiohttp.ClientSession | None] = None
    name = "http"

    @classmethod
    async def start(cls, env: dict[str, str]):
        cls._instance = aiohttp.ClientSession()
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.close()
        cls._instance = None
        return cls

    async def __aenter__(self) -> aiohttp.ClientSession:
        return self._instance

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass


class DBEngine(dependency.Dependency[AsyncEngine]):
    _instance: ClassVar[AsyncEngine | None] = None
    name = "db"

    @classmethod
    async def start(cls, env: dict[str, str]):
        url = (
            f"postgresql+asyncpg://"
            f"{env.get('DBUSER')}"
            f"@{env.get('DBHOST')}"
            f":{env.get('DBPORT')}"
            f"/{env.get('DBNAME')}"
        )
        cls._instance = create_async_engine(url)
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls._instance.dispose()
        cls._instance = None
        return cls

    async def __aenter__(self) -> AsyncEngine:
        return self._instance

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass


core_dependencies = [DBEngine,]
