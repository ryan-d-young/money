from asyncio import AbstractEventLoop
from typing import ClassVar

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .dependency import Dependency


class DBEngine(Dependency[AsyncEngine]):
    instance: ClassVar[AsyncEngine | None] = None
    name = "db"

    @classmethod
    async def start(cls, env: dict[str, str], loop: AbstractEventLoop):
        url = f"postgresql+asyncpg://{env.get('DBUSER')}@{env.get('DBHOST')}:{env.get('DBPORT')}/{env.get('DBNAME')}"
        cls.instance = create_async_engine(url)
        return cls

    @classmethod
    async def stop(cls, env: dict[str, str]):
        await cls.instance.dispose()
        cls.instance = None
        return cls

    async def __aenter__(self) -> AsyncEngine:
        return self.instance

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass
