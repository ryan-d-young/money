import httpx
from typing import ClassVar
from asyncio import AbstractEventLoop
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .core import dependency


class HttpClient(dependency.Dependency[httpx.AsyncClient]):
    _instance: ClassVar[httpx.AsyncClient | None] = None
    name = "http"

    @classmethod
    async def start(cls, env: dict[str, str], loop: AbstractEventLoop):
        cls._instance = httpx.AsyncClient(verify=False)
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        if cls._instance:
            await cls._instance.aclose()
            cls._instance = None
        return cls

    async def __aenter__(self) -> httpx.AsyncClient:
        return self._instance

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass


class DBEngine(dependency.Dependency[AsyncEngine]):
    _instance: ClassVar[AsyncEngine | None] = None
    name = "db"

    @classmethod
    async def start(cls, env: dict[str, str], loop: AbstractEventLoop):
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
