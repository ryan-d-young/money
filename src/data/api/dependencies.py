import aiohttp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .core.protocols import Dependency


class ClientSession(Dependency):
    _instance: aiohttp.ClientSession
    async def start(self, env: dict[str, str]):
        self._instance = aiohttp.ClientSession()

    async def stop(self, env: dict[str, str]):
        await self._instance.close()
        self._instance = None
        

class DBEngine(Dependency):
    _instance: AsyncEngine
    async def start(self, env: dict[str, str]):
        url = f"postgresql+asyncpg://{env['dbuser']}:{env['dbpass']}@{env['dbhost']}:{env['dbport']}"
        self._instance = create_async_engine(url)

    async def stop(self, env: dict[str, str]):
        await self._instance.dispose()
        self._instance = None
        